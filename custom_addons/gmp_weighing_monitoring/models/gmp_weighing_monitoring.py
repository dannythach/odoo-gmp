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

    # Thêm trường này vào model gmpweighingmonitoring
    log_date = fields.Date(
        string="Ngày ghi nhận",
        compute="_compute_log_date",
        store=True
    )

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

    line_id = fields.Many2one(
        comodel_name="base.line",
        string="Dây chuyền",
        required=True
    )
    linecode = fields.Char(
        related="line_id.code",
        string="Mã dây chuyền",
        store=True,
        readonly=True
    )
    linename = fields.Char(
        related="line_id.name",
        store=True,
        string="Tên dây chuyền",
        readonly=True
    )

    shift_id = fields.Many2one(
        comodel_name="base.shift",
        string="Ca",
        required=True
    )
    shiftcode = fields.Char(
        related="shift_id.code",
        string="Mã ca",
        store=True,
        readonly=True
    )
    shiftname = fields.Char(
        related="shift_id.name",
        store=True,
        string="Tên ca",
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

    # Nguyên phụ liệu
    material_id = fields.Many2one(
        comodel_name="gmp.oitm",
        string="Nguyên phụ liệu",
        required=True,
        domain="[('id', 'in', allowed_material_ids)]"
    )
    materialcode = fields.Char(
        related="material_id.itemcode",
        string="Mã nguyên phụ liệu",
        store=True,
        readonly=True
    )
    materialname = fields.Char(
        related="material_id.itemname",
        string="Tên nguyên phụ liệu",
        store=True,
        readonly=True
    )
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

    # Lô, mẻ
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    bom_quantity = fields.Float(string="SL theo BOM/Định mức")
    actual_quantity = fields.Float(string="SL thực cân", required=True)
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

    # tạo field tạm chứa allowed items
    allowed_item_ids = fields.Many2many(
        'gmp.oitm',
        compute='_compute_allowed_items',
        store=False
    )

    allowed_material_ids = fields.Many2many(
        'gmp.oitm',
        compute='_compute_allowed_materials',
        store=False
    )

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
    
    # compute
    # item_id
    @api.depends('productionplan_id','line_id','shift_id')
    def _compute_allowed_items(self):
        for record in self:
            if not record.productionplan_id or not record.line_id or not record.shift_id:
                record.allowed_item_ids = [(5, 0, 0)]
                continue

            plan_details = self.env['base.daily.production.plan.detail'].search([
                ('docentry', '=', record.productionplan_id.docentry),
                ('u_oriline', '=', record.line_id.code), # Hoặc id tùy vào kiểu dữ liệu của u_line
                ('u_shift', '=', record.shift_id.code) # Hoặc id tùy vào kiểu dữ liệu của u_line
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

    # material_id        
    @api.depends('productionplan_id')
    def _compute_allowed_materials(self):
        for record in self:
            if not record.productionplan_id:
                record.allowed_material_ids = [(5, 0, 0)]
                continue

            materials = self.env['base.material.detail'].search([
                ('docnum', '=', record.productionplan_id.docnum)
            ])

            codes = list(set([
                str(code).strip()
                for code in materials.mapped('materialcode')
                if code
            ]))

            items = self.env['gmp.oitm'].search([
                ('itemcode', 'in', codes)
            ])

            record.allowed_material_ids = items

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

        # 2. KIỂM TRA NGUYÊN PHỤ LIỆU
        # Nếu chưa chọn Material thì dừng các bước tính toán BOM/UOM phía dưới
        if not self.material_id:
            self.uom_id = False
            self.bom_quantity = 0.0
            return

        # 3. Load UOM
        if self.material_id.iuomcode:
            uom = self.env['gmp.ouom'].search([('uomcode', '=', self.material_id.iuomcode)], limit=1)
            if uom:
                self.uom_id = uom

        # 4. Load BOM dựa trên docnum và itemcode
        if self.productionplan_id and self.material_id:
            material = self.env['base.material.detail'].search([
                ('materialcode', '=', self.material_id.itemcode),
                ('docnum', '=', self.productionplan_id.docnum)
            ], limit=1)

            if material:
                self.bom_quantity = material.materialqty
            else:
                self.bom_quantity = 0.0
        else:
            self.bom_quantity = 0.0
    
    # Hàm xử lý lọc lại Plan khi chọn lại ngày
    @api.depends('log_datetime')
    def _compute_log_date(self):
        for record in self:
            if record.log_datetime:
                # Chuyển đổi datetime thành date để so sánh chính xác trong XML domain
                record.log_date = record.log_datetime.date()
            else:
                record.log_date = False

    # Cập nhật lại hàm onchange để dùng trường mới
    @api.onchange('log_datetime')
    def _onchange_log_datetime_filter_plan(self):
        self.productionplan_id = False 
        if self.log_datetime:
            # Trả về domain dựa trên Date thay vì Datetime
            return {
                'domain': {
                    'productionplan_id': [('u_docdate', '=', self.log_datetime.date())]
                }
            }      
    
         
