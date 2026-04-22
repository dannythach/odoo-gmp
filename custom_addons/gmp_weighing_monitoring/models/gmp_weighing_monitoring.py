from odoo import models, fields, api

class GmpWeighingMonitoring(models.Model):
    _name = "gmp.weighing.monitoring"
    _description = "Chuẩn bị và cân định lượng NPL (Header)"
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
    itemcode = fields.Char(related="item_id.itemcode", readonly=True)
    itemname = fields.Char(related="item_id.itemname", readonly=True)

    fromts = fields.Integer(
        string="Từ TS", 
        compute="_compute_header_ts_values", # Tên hàm ở đây
        store=True
    )
    tots = fields.Integer(
        string="Đến TS", 
        compute="_compute_header_ts_values", # Tên hàm ở đây
        store=True
    )

    line_ids = fields.One2many(
        comodel_name="gmp.weighing.monitoring.line",
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

    # --- HÀM MỞ WIZARD (CỐ ĐỊNH LỖI TRÊN HEADER) ---
    def action_open_weighing_wizard(self):
        """Hàm mở Wizard cho nút Thêm dòng nhanh (Mobile)"""
        self.ensure_one()
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.weighing.monitoring.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.id,
                'default_valid_item_ids': self.valid_item_ids.ids,
                'default_valid_material_ids': self.valid_material_ids.ids,
                'default_line_id': False,
            }
        }


class GmpWeighingMonitoringLine(models.Model):
    _name = "gmp.weighing.monitoring.line"
    _description = "Chi tiết cân định lượng (Lines)"

    header_id = fields.Many2one('gmp.weighing.monitoring', ondelete="cascade")
    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)
    material_id = fields.Many2one('gmp.oitm', string="Nguyên phụ liệu", required=True)
    materialcode = fields.Char(related="material_id.itemcode", readonly=True)
    materialname = fields.Char(related="material_id.itemname", readonly=True)
    uom_id = fields.Many2one('gmp.ouom', string="Đơn vị tính", required=True)
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    bom_quantity = fields.Float(string="SL Định mức")
    actual_quantity = fields.Float(string="SL Thực cân", required=True)
    quantity_variance = fields.Float(string="Chênh lệch", compute="_compute_quantity_variance", store=True)
    result = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Kết quả", default="Pass")
    note = fields.Text(string="Ghi chú")


    @api.onchange('material_id')
    def _onchange_material_id_load_data(self):
        for record in self:
            # reset
            record.uom_id = False
            record.bom_quantity = 0

            if not record.material_id:
                return

            # 1. Load đơn vị tính từ item master
            record.uom_id = self.env['gmp.ouom'].search([('uomcode', '=', self.material_id.iuomcode)], limit=1)

            # 2. Lấy header
            header = record.header_id or self.env['gmp.weighing.monitoring'].browse(
                self._context.get('active_id')
            )

            if not header or not header.productionplan_id or not record.item_id:
                return

            # 3. Lấy định mức từ BOM / material detail
            material_detail = self.env['base.material.detail'].search([
                ('docnum', '=', header.productionplan_id.docnum),
                ('materialcode', '=', record.material_id.itemcode), # nếu có field này
            ], limit=1)

            if material_detail:
                record.bom_quantity = material_detail.materialqty or 0

    @api.depends("bom_quantity", "actual_quantity")
    def _compute_quantity_variance(self):
        for record in self:
            record.quantity_variance = record.actual_quantity - record.bom_quantity

    def action_edit_line(self):
        """Hàm mở Wizard để sửa dòng hiện tại"""
        self.ensure_one()
        return {
            'name': 'Chỉnh sửa chi tiết cân',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.weighing.monitoring.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
                'default_line_id': self.id,
                'default_material_id': self.material_id.id,
                'default_actual_quantity': self.actual_quantity,
                'default_lot_code': self.lot_code,
                'default_batch_code': self.batch_code,
                'default_result': self.result,
                'default_note': self.note,
                'default_log_datetime': self.log_datetime,
                'default_valid_item_ids': self.header_id.valid_item_ids.ids,
                'default_valid_material_ids': self.header_id.valid_material_ids.ids,
            }
        }
    
    # --- HÀM BỔ SUNG ĐỂ SỬA LỖI XML ---
    def action_open_weighing_wizard(self):
        """
        Hàm cầu nối: Khi bấm nút trong thẻ <control> của danh sách Line, 
        nó sẽ gọi hàm của model cha (Header).
        """
        # Lấy context từ model cha để đảm bảo dữ liệu valid_ids được truyền đúng
        monitoring = self.env['gmp.weighing.monitoring'].browse(self._context.get('active_id'))
        if not monitoring:
            # Trường hợp bản ghi mới chưa lưu, lấy qua field Many2one
            monitoring = self.header_id
            
        return monitoring.action_open_weighing_wizard()

