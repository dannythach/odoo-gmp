from odoo import models, fields, api

class gmpcutting(models.Model):
    _name = "gmp.cutting"
    _description = "Hấp"
    _order = "log_datetime desc"
    _rec_name = 'note'

    log_datetime = fields.Datetime(
        string="Thời gian",
        default=fields.Datetime.now,
        required=True
    )

    # Liên kết với kế hoạch sản xuất
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
        string="Ghi chú",
        store=True,
        readonly=True
    )
    
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

    # Thành phẩm
    item_id = fields.Many2one(
        comodel_name="gmp.oitm",
        string="Sản phẩm",
        required=True,
        domain="[('id', 'in', allowed_item_ids)]"
    )
    itemcode = fields.Char(
        related="item_id.itemcode",
        string="Mã sản phẩm",
        store=True,
        readonly=True
    )
    itemname = fields.Char(
        related="item_id.itemname",
        string="Tên sản phẩm",
        store=True,
        readonly=True
    )
    fromts = fields.Integer(
        string="Từ TS",
        readonly=True,
        help="Lấy từ dòng đầu tiên của kế hoạch sản xuất tương ứng với thành phẩm"
    )
    tots = fields.Integer(
        string="Đến TS",
        readonly=True,
        help="Lấy từ dòng đầu tiên của kế hoạch sản xuất tương ứng với thành phẩm"
    )

    # Lô, mẻ
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    noodle_length = fields.Float(string="Chiều dài sợi mì (cm)")
    standard_weight = fields.Float(string="KL/TL quy định (g)")
    actual_weight = fields.Float(string="KL/ TL đo (g)")
    cutting_speed = fields.Float(string="Tốc độ dao cắt (lần/p)")
    conveyor_speed = fields.Char(string="Vận tốc băng tải")
    post_cutting_status = fields.Float(string="Tình trạng vắt mì sau cắt định lượng")
    
    result = fields.Selection(
        [
            ("Pass", "Đạt"),
            ("Fail", "Không đạt"),
        ],
        string="Kết quả",
        default="Pass"
    )

    operator = fields.Many2one(
        comodel_name="res.users",
        string="Người vận hành",
        default=lambda self: self.env.user
    )
    
    note = fields.Text(string="Ghi chú")

    # tạo field tạm chứa allowed items
    allowed_item_ids = fields.Many2many(
        'gmp.oitm',
        compute='_compute_allowed_items',
        store=False
    )

    # --- CÁC HÀM XỬ LÝ LOGIC ---

    @api.depends('productionplan_id')
    def _compute_productionplanfactory(self):
        for record in self:
            if record.productionplan_id:
                record.productionplanfactory = record.productionplan_id.u_factory
            else:
                record.productionplanfactory = False

    # compute
    # item_id
    @api.depends('productionplan_id')
    def _compute_allowed_items(self):
        for record in self:
            if not record.productionplan_id:
                record.allowed_item_ids = [(5, 0, 0)]
                continue

            plan_details = self.env['base.daily.production.plan.detail'].search([
                ('docentry', '=', record.productionplan_id.docentry)
            ])

            codes = list(set([
                str(code).strip()
                for code in plan_details.mapped('u_itemcode')
                if code
            ]))

            items = self.env['gmp.oitm'].search([
                ('itemcode', 'in', codes)
            ])

            record.allowed_item_ids = items
   
    # CÁC HÀM ONCHANGE DUY NHẤT ĐỂ LOAD DỮ LIỆU     
    @api.onchange('item_id','material_id', 'productionplan_id')
    def _onchange_load_data(self):
        # 1. LOAD FROMTS, TOTS TỪ THÀNH PHẨM (ITEM_ID) ---
        if self.productionplan_id and self.item_id:
            # Tìm dòng đầu tiên trong bảng chi tiết của kế hoạch khớp với mã thành phẩm
            # Giả sử model chi tiết kế hoạch là 'base.daily.production.plan.detail'
            prod_detail = self.env['base.daily.production.plan.detail'].search([
                ('docentry', '=', self.productionplan_id.docentry), # Liên kết qua docentry hoặc id tùy model của bạn
                ('u_itemcode', '=', self.item_id.itemcode)
            ], limit=1, order='id asc') # Lấy dòng đầu tiên
            
            if prod_detail:
                self.fromts = prod_detail.u_fromts
                self.tots = prod_detail.u_tots
            else:
                self.fromts = 0
                self.tots = 0
        else:
            self.fromts = 0
            self.tots = 0 

    # @api.onchange('search_docnum')
    # def _onchange_search_docnum(self):
    #     """Tìm kế hoạch sản xuất dựa trên số DocNum nhập vào"""
    #     if self.search_docnum:
    #         try:
    #             docnum_val = int(self.search_docnum)
    #             plan = self.env['base.daily.production.plan'].search([
    #                 ('docnum', '=', docnum_val)
    #             ], limit=1)
    #             if plan:
    #                 self.productionplan_id = plan.id
    #         except ValueError:
    #             pass
