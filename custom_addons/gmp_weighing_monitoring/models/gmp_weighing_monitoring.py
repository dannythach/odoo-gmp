from odoo import models, fields, api

class gmpweighingmonitoring(models.Model):
    _name = "gmp.weighing.monitoring"
    _description = "Chuẩn bị và cân định lượng NPL"
    _order = "log_datetime desc"
    _rec_name = 'note'

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
        string="Kế hoạch sản xuất",
        store=True,
        readonly=True
    )
    productionplanname = fields.Char(
        related="productionplan_id.remark",
        store=True,
        string="Ghi chú",
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
    # uom = fields.Char(string="ĐVT")
    bom_quantity = fields.Float(string="SL theo BOM/Định mức")
    actual_quantity = fields.Float(string="SL thực cân", required=True)
    # quantity_variance = fields.Float(string="Chênh lệch SL", compute="_compute_quantity_variance")
    quantity_variance = fields.Float(
        string="Chênh lệch SL",
        compute="_compute_quantity_variance",
        store=True
    )
    
    # Tình trạng bảo quản sau cân - định lượng
    post_weighing_status = fields.Selection(
        [
            ("Good", "Tốt"),
            ("Bad", "Kém"),
        ],
        string="Bảo quản",
        default="Good"
    )

    # Nhân diện sau cân - định lượng
    post_weighing_identification = fields.Selection(
        [
            ("Yes", "C"),
            ("No", "K"),
        ],
        string="Nhân diện",
        default="Yes"
    )

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

    @api.depends("bom_quantity", "actual_quantity")
    def _compute_quantity_variance(self):
        for record in self:
            record.quantity_variance = (record.actual_quantity or 0.0) - (record.bom_quantity or 0.0)

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

        # 2. Load BOM dựa trên docnum và itemcode
        if self.productionplan_id and self.item_id:
            material = self.env['base.material.detail'].search([
                ('materialcode', '=', self.item_id.itemcode),
                ('docnum', '=', self.productionplan_id.docnum)
            ], limit=1)

            if material:
                self.bom_quantity = material.materialqty
            else:
                self.bom_quantity = 0.0
        else:
            self.bom_quantity = 0.0
