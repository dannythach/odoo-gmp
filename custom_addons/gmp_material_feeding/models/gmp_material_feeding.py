from odoo import models, fields, api

class gmpmaterialfeeding(models.Model):
    _name = "gmp.material.feeding"
    _description = "Cấp / nạp liệu chế biến"
    _order = "log_date desc"
    _rec_name = 'productionplanname'

    # --- THÔNG TIN HEADER ---
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
    
    productionplancode = fields.Integer(related="productionplan_id.docnum", string="Mã kế hoạch", readonly=True)
    productionplanname = fields.Char(related="productionplan_id.remark", string="Ghi chú kế hoạch", readonly=True)
    
    productionplanfactory = fields.Selection(
        selection=[
            ('01', 'Mì'), ('02', 'Phở'), ('03', 'Nêm'),
            ('04', 'Đóng gói'), ('05', 'Nấu dầu - Soup trộn'),
        ],
        string="Xưởng",
        compute="_compute_productionplanfactory",
        store=True
    )

    line_id = fields.Many2one(comodel_name="base.line", string="Dây chuyền", required=True)
    linecode = fields.Char(related="line_id.code", string="Mã dây chuyền", readonly=True)
    linename = fields.Char(related="line_id.name", string="Tên dây chuyền", readonly=True)
    
    shift_id = fields.Many2one(comodel_name="base.shift", string="Ca", required=True)
    shiftcode = fields.Char(related="shift_id.code", string="Mã ca", readonly=True)
    shiftname = fields.Char(related="shift_id.name", string="Tên ca", readonly=True)

    # Quan hệ với bảng chi tiết
    line_ids = fields.One2many(
        'gmp.material.feeding.line', 
        'header_id', 
        string="Chi tiết nạp liệu"
    )

    # Các trường ẩn để hỗ trợ domain lọc trong Line
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

    # --- HÀM MỞ WIZARD (CỐ ĐỊNH LỖI TRÊN HEADER) ---
    def action_open_weighing_wizard(self):
        """Hàm mở Wizard cho nút Thêm dòng nhanh (Mobile)"""
        self.ensure_one()
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.material.feeding.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_monitoring_id': self.id,
                'default_valid_item_ids': self.valid_item_ids.ids,
                'default_valid_material_ids': self.valid_material_ids.ids,
                'default_line_id': False,
            }
        }        

# --- MODEL CHI TIẾT (LINES) ---
class gmpmaterialfeedingline(models.Model):
    _name = "gmp.material.feeding.line"
    _description = "Chi tiết cấp / nạp liệu"

    header_id = fields.Many2one('gmp.material.feeding', string="Feeding Reference", ondelete='cascade')
    
    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)

    # Thành phẩm
    item_id = fields.Many2one('gmp.oitm', string="Sản phẩm", required=True)
    fromts = fields.Integer(string="Từ TS", readonly=True)
    tots = fields.Integer(string="Đến TS", readonly=True)

    # Nguyên phụ liệu
    material_id = fields.Many2one('gmp.oitm', string="Nguyên phụ liệu", required=True)
    materialname = fields.Char(related="material_id.itemname", readonly=True)
    uom_id = fields.Many2one('gmp.ouom', string="ĐVT")
    
    # Định mức & Thực tế
    bom_quantity = fields.Float(string="SL BOM")
    actual_quantity = fields.Float(string="SL Thực tế", required=True)
    quantity_variance = fields.Float(string="Chênh lệch", compute="_compute_variance", store=True)

    # Trạng thái & Kết quả (Selection)
    cip = fields.Selection([("C", "Đạt"), ("K", "Không đạt")], string="CIP", default="C")
    cop = fields.Selection([("C", "Đạt"), ("K", "Không đạt")], string="COP", default="C")
    cleanliness_status = fields.Selection([("S", "Sạch"), ("K", "Không đạt")], string="Vệ sinh", default="S")
    operating_status = fields.Selection([("Đ", "Đạt"), ("K", "Không đạt")], string="Thao tác", default="Đ")
    final_result = fields.Selection([("Đ", "Đạt"), ("K", "Không đạt")], string="Kết quả", default="Đ")

    operator = fields.Many2one('res.users', string="Người nạp", default=lambda self: self.env.user)
    note = fields.Text(string="Ghi chú")

    @api.depends('actual_quantity', 'bom_quantity')
    def _compute_variance(self):
        for line in self:
            line.quantity_variance = (line.actual_quantity or 0.0) - (line.bom_quantity or 0.0)

    @api.onchange('item_id', 'material_id')
    def _onchange_load_data(self):
        if not self.header_id: return
        
        # Load FromTS/ToTS
        if self.item_id and self.header_id.productionplan_id:
            detail = self.env['base.daily.production.plan.detail'].search([
                ('docentry', '=', self.header_id.productionplan_id.docentry),
                ('u_itemcode', '=', self.item_id.itemcode)
            ], limit=1)
            self.fromts = detail.u_fromts if detail else 0
            self.tots = detail.u_tots if detail else 0

        # Load BOM & UOM
        if self.material_id:
            if self.material_id.iuomcode:
                self.uom_id = self.env['gmp.ouom'].search([('uomcode', '=', self.material_id.iuomcode)], limit=1)
            
            material_bom = self.env['base.material.detail'].search([
                ('materialcode', '=', self.material_id.itemcode),
                ('docnum', '=', self.header_id.productionplan_id.docnum)
            ], limit=1)
            self.bom_quantity = material_bom.materialqty if material_bom else 0.0