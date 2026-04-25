from odoo import models, fields, api

class GmpSlittingWaving(models.Model):
    _name = "gmp.slitting.waving"
    _description = "Cắt sợi và tạo sóng (Header)"
    _order = "log_date desc"
    _rec_name = 'productionplancode'

    log_date = fields.Date(
        string="Ngày ghi nhận",
        default=fields.Date.context_today,
        required=True
    )

    productionplan_id = fields.Many2one(
        comodel_name="base.daily.production.plan",
        string="Kế hoạch sản xuất (Plan)",
        required=True
    )

    productionplancode = fields.Integer(related="productionplan_id.docnum", string="Số kế hoạch", store=True, readonly=True)
    productionplanname = fields.Char(related="productionplan_id.remark", string="Ghi chú kế hoạch", readonly=True)
    
    productionplanfactory = fields.Selection(
        selection=[('01', 'Mì'), ('02', 'Phở'), ('03', 'Nêm'), ('04', 'Đóng gói'), ('05', 'Nấu dầu - Soup trộn')],
        string="Xưởng",
        compute="_compute_productionplanfactory",
        store=True,
        readonly=True
    )

    line_id = fields.Many2one(comodel_name="base.line", string="Dây chuyền", required=True)
    linecode = fields.Char(related="line_id.code", string="Mã dây chuyền", readonly=True)
    linename = fields.Char(related="line_id.name", string="Tên dây chuyền", readonly=True)

    area = fields.Char(string="Khu vực")

    shift_id = fields.Many2one(comodel_name="base.shift", string="Ca", required=True)
    shiftcode = fields.Char(related="shift_id.code", string="Mã ca", readonly=True)
    shiftname = fields.Char(related="shift_id.name", string="Tên ca", readonly=True)

    group = fields.Char(string="Tổ")

    item_id = fields.Many2one('gmp.oitm', string="Sản phẩm", required=True)
    itemcode = fields.Char(related="item_id.itemcode", string="Mã sản phẩm", readonly=True)
    itemname = fields.Char(related="item_id.itemname", string="Tên sản phẩm", readonly=True)

    fromts = fields.Integer(
        string="Từ", 
        compute="_compute_header_ts_values", # Tên hàm ở đây
        store=True
    )
    tots = fields.Integer(
        string="Đến", 
        compute="_compute_header_ts_values", # Tên hàm ở đây
        store=True
    )

    fromts_display = fields.Float(string="Từ", compute="_compute_time_display")
    tots_display = fields.Float(string="Đến", compute="_compute_time_display")

    dough_sheet = fields.Float(string="Tấm bột (QC/Kich thước)(mm)")
    conveyor_belt = fields.Char(string="Băng tải")

    line_ids = fields.One2many(
        comodel_name="gmp.slitting.waving.line",
        inverse_name="header_id",
        string="Chi tiết các dòng cân"
    )

    valid_item_ids = fields.Many2many(
        comodel_name='gmp.oitm', 
        compute='_compute_valid_item_ids',
        string="Valid Items"
    )

    valid_material_ids = fields.Many2many(
        comodel_name='gmp.oitm', 
        compute='_compute_valid_material_ids',
        string="Valid Materials"
    )
    
    # --- CÁC HÀM COMPUTE ---
    @api.depends('productionplan_id')
    def _compute_productionplanfactory(self):
        for record in self:
            record.productionplanfactory = record.productionplan_id.u_factory if record.productionplan_id else False

    @api.onchange('log_date')
    def _onchange_log_date_filter_plan(self):
        self.productionplan_id = False 
        if self.log_date:
            return {'domain': {'productionplan_id': [('u_docdate', '=', self.log_date)]}}

    @api.depends('productionplan_id', 'line_id', 'shift_id')
    def _compute_valid_item_ids(self):
        for record in self:
            if record.productionplan_id and record.line_id and record.shift_id:
                plan_details = self.env['base.daily.production.plan.detail'].search([
                    ('docentry', '=', record.productionplan_id.docentry),
                    ('u_oriline', '=', record.line_id.code),
                    ('u_shift', '=', record.shift_id.code)
                ])
                item_codes = plan_details.mapped('u_itemcode')
                items = self.env['gmp.oitm'].search([('itemcode', 'in', item_codes)])
                record.valid_item_ids = [(6, 0, items.ids)]
            else:
                record.valid_item_ids = [(5, 0, 0)]

    @api.depends('productionplan_id')
    def _compute_valid_material_ids(self):
        for record in self:
            if not record.productionplan_id:
                record.valid_material_ids = [(5, 0, 0)]
                continue
            materials = self.env['base.material.detail'].search([
                ('docnum', '=', record.productionplan_id.docnum)
            ])
            codes = list(set([str(code).strip() for code in materials.mapped('materialcode') if code]))
            items = self.env['gmp.oitm'].search([('itemcode', 'in', codes)])
            record.valid_material_ids = items
    
    @api.depends('item_id', 'productionplan_id', 'line_id', 'shift_id')
    def _compute_header_ts_values(self): # Tên hàm phải khớp với khai báo trên field
        for record in self:
            if not record.item_id or not record.productionplan_id:
                record.fromts = 0
                record.tots = 0
                continue

            plan_detail = self.env['base.daily.production.plan.detail'].search([
                ('docentry', '=', record.productionplan_id.docentry),
                ('u_itemcode', '=', record.item_id.itemcode),
                ('u_oriline', '=', record.line_id.code),
                ('u_shift', '=', record.shift_id.code)
            ], limit=1)

            if plan_detail:
                record.fromts = plan_detail.u_fromts or 0
                record.tots = plan_detail.u_tots or 0
            else:
                record.fromts = 0
                record.tots = 0

    @api.depends('fromts', 'tots')
    def _compute_time_display(self):
        for record in self:
            
            if record.fromts:
                hours = record.fromts // 100
                minutes = record.fromts % 100
                record.fromts_display = hours + (minutes / 60.0)
            else:
                record.fromts_display = 0.0
                
            if record.tots:
                hours = record.tots // 100
                minutes = record.tots % 100
                record.tots_display = hours + (minutes / 60.0)
            else:
                record.tots_display = 0.0            

    # --- HÀM MỞ WIZARD (CỐ ĐỊNH LỖI TRÊN HEADER) ---
    def action_open_slitting_waving_wizard(self):
        """Hàm mở Wizard cho nút Thêm dòng nhanh (Mobile)"""
        self.ensure_one()
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.slitting.waving.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.id,
                'default_valid_item_ids': self.valid_item_ids.ids,
                'default_valid_material_ids': self.valid_material_ids.ids,
                'default_line_id': False,
            }
        }


class GmpSlittingWavingLine(models.Model):
    _name = "gmp.slitting.waving.line"
    _description = "Cắt sợi và tạo sóng (Lines)"

    header_id = fields.Many2one('gmp.slitting.waving', ondelete="cascade")
    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    slitter_id = fields.Char(string="Mã số dao cắt")
    noodle_diameter = fields.Float(string="Đường kính sợi mì (mm)")
    slitter_speed = fields.Float(string="Vận tốc dao cắt (m/s)")
    noodle_speed = fields.Float(string="Vận tốc sợi mì (m/s) ")
    noodle_density = fields.Char(string="Mật độ sợi/độ đều sợi")
    noodle_surface = fields.Char(string="Bề mặt sợi")
    wave_amplitude = fields.Char(string="Biên độ sóng")
    
    result = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Kết quả", default="Pass")
    operator = fields.Many2one(
        comodel_name="res.users",
        string="Người vận hành",
        default=lambda self: self.env.user
    )
    note = fields.Text(string="Ghi chú")

    @api.onchange('material_id')
    def _onchange_material_id_load_data(self):
        for record in self:
            # reset
            record.uom_id = False
            record.bom_quantity = 0

            if not record.material_id:
                return

            # 2. Lấy header
            header = record.header_id or self.env['gmp.slitting.waving'].browse(
                self._context.get('active_id')
            )

            if not header or not header.productionplan_id or not record.item_id:
                return

    def action_edit_line(self):
        """Hàm mở Wizard để sửa dòng hiện tại"""
        self.ensure_one()
        return {
            'name': 'Chỉnh sửa chi tiết',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.slitting.waving.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
                'default_line_id': self.id,
                'default_lot_code': self.lot_code,
                'default_batch_code': self.batch_code,
                
                'default_slitter_id': self.slitter_id,
                'default_noodle_diameter': self.noodle_diameter,
                'default_slitter_speed': self.slitter_speed,
                'default_noodle_speed': self.noodle_speed,
                'default_noodle_density': self.noodle_density,
                'default_noodle_surface': self.noodle_surface,
                'default_wave_amplitude': self.wave_amplitude,
                
                'default_result': self.result,
                'default_operator': self.operator.id,
                'default_note': self.note,
                'default_log_datetime': self.log_datetime,
                'default_valid_item_ids': self.header_id.valid_item_ids.ids,
                'default_valid_material_ids': self.header_id.valid_material_ids.ids,
            }
        }
    
    # --- HÀM BỔ SUNG ĐỂ SỬA LỖI XML ---
    def action_open_slitting_waving_wizard(self):
        """
        Hàm cầu nối: Khi bấm nút trong thẻ <control> của danh sách Line, 
        nó sẽ gọi hàm của model cha (Header).
        """
        # Lấy context từ model cha để đảm bảo dữ liệu valid_ids được truyền đúng
        monitoring = self.env['gmp.slitting.waving'].browse(self._context.get('active_id'))
        if not monitoring:
            # Trường hợp bản ghi mới chưa lưu, lấy qua field Many2one
            monitoring = self.header_id
            
        return monitoring.action_open_slitting_waving_wizard()

