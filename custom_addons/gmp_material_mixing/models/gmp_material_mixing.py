from odoo import models, fields, api

class gmpmaterialmixing(models.Model):
    _name = "gmp.material.mixing"
    _description = "Nhào trộn NPL"
    _order = "log_datetime desc"

    log_datetime = fields.Datetime(
        string="Thời gian",
        default=fields.Datetime.now,
        required=True
    )

    #itemcode = fields.Char(string="Mã NPL", required=True)
    #itemname = fields.Char(string="Tên NPL", required=True)
    productionplan_id = fields.Many2one(
        comodel_name="base.daily.production.plan",
        string="Plan",
        required=True
    )
    productionplancode = fields.Integer(
        related="productionplan_id.docnum",
        store=True,
        readonly=True
    )
    productionplanname = fields.Char(
        related="productionplan_id.remark",
        store=True,
        readonly=True
    )
    # Sửa lại trường này, bỏ related Char cũ
    productionplanfactory = fields.Selection(
        selection=[
            ('01', 'Mì'),
            ('02', 'Phở'),
            ('03', 'Nêm'),
            ('04', 'Đóng gói'),
            ('05', 'Nấu dầu - Soup trộn'),
        ],
        string="Xưởng",
        compute="_compute_productionplanfactory",
        store=True,
        readonly=True
    )

    item_id = fields.Many2one(
        comodel_name="gmp.oitm",
        string="Nguyên phụ liệu",
        required=True
    )
    itemcode = fields.Char(
        related="item_id.itemcode",
        store=True,
        readonly=True
    )
    itemname = fields.Char(
        related="item_id.itemname",
        store=True,
        readonly=True
    )
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    uom_id = fields.Many2one(
        comodel_name="gmp.ouom",
        string="Đơn vị tính",
        required=True
    )
    uomcode = fields.Char(
        related="uom_id.uomcode",
        store=True,
        readonly=True
    )
    uomname = fields.Char(
        related="uom_id.uomname",
        store=True,
        readonly=True
    )

    equipment_code = fields.Char(string="Mã số thiết bị")
    mixing_time = fields.Float(string="Thời gian nhào trộn (phút)")
    dough_temperature = fields.Float(string="Nhiệt độ khối bột sau trộn (°C)")
    dough_status = fields.Char(string="Trạng thái mẻ bột, khối bột")
    
    result = fields.Selection(
        [
            ("Pass", "Đạt"),
            ("Fail", "Không đạt"),
        ],
        string="Kết quả",
        default="Pass"
    )

    # operator = fields.Char(string="Người vận hành")
    operator = fields.Many2one(
        comodel_name="res.users",
        string="Người vận hành",
        default=lambda self: self.env.user
    )
    note = fields.Text(string="Ghi chú")

    # --- CÁC HÀM XỬ LÝ LOGIC ---

    @api.depends('productionplan_id')
    def _compute_productionplanfactory(self):
        for record in self:
            if record.productionplan_id:
                record.productionplanfactory = record.productionplan_id.u_factory
            else:
                record.productionplanfactory = False

    # HÀM ONCHANGE DUY NHẤT ĐỂ LOAD DỮ LIỆU
    @api.onchange('item_id', 'productionplan_id')
    def _onchange_load_data(self):
        if not self.item_id:
            return

        # 1. Load UOM
        if self.item_id.iuomcode:
            uom = self.env['gmp.ouom'].search([('uomcode', '=', self.item_id.iuomcode)], limit=1)
            if uom:
                self.uom_id = uom
