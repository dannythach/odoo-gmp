from odoo import models, fields, api

class gmpmoldingadjustment(models.Model):
    _name = "gmp.molding.adjustment"
    _description = "Sửa khuôn"
    _order = "log_datetime desc"
    _rec_name = 'note'

    log_datetime = fields.Datetime(
        string="Thời gian",
        default=fields.Datetime.now,
        required=True
    )

    # Thêm trường này vào model gmpmoldingadjustment
    log_date = fields.Date(
        string="Ngày ghi nhận",
        compute="_compute_log_date",
        store=True
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

    # Lô, mẻ
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    mold_code = fields.Char(string="Loại khuôn (Mã số)")
    adjustment_stick_diameter = fields.Float(string="Đường kính đũa (mm)")
    adjustment_stick_length = fields.Float(string="Chiều dài đũa (mm)")
    distance_stick_mold = fields.Float(string="K/C chỉnh đũa & khuôn (mm)")
    air_flow_rate = fields.Float(string="Hơi khí nén (m³/p)")
    air_pressure = fields.Float(string="Hơi khí nén (bar)")
    fan_speed = fields.Float(string="Vận tốc cánh quạt (v/p)")
    fan_wind_speed = fields.Float(string="Vận tốc gió (m/s)")

    # Tình trạng BTP sau sửa
    sfp_status  = fields.Char(string="Tình trạng BTP sau sửa")
    
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
    
    def copy(self, default=None):
        """
        Ghi đè hàm copy để khi nhân bản:
        1. Lấy thời gian hiện tại (mới nhất).
        2. Các dữ liệu khác giữ nguyên từ bản ghi cũ.
        """
        default = dict(default or {})
        
        # Cập nhật log_datetime là thời gian hiện tại
        default.update({
            'log_datetime': fields.Datetime.now(),
            # 'log_date': fields.Date.today(),
        })
        return super(gmpmoldingadjustment, self).copy(default)
    
    def action_cron_duplicate_latest(self):
        """Hàm dành cho Scheduled Action để nhân bản bản ghi gần nhất"""
        # Tìm bản ghi mới nhất dựa trên thời gian ghi nhận
        latest_record = self.search([], order='log_datetime desc', limit=1)
        if latest_record:
            # Gọi hàm copy đã ghi đè phía dưới
            latest_record.copy()
