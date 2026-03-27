from odoo import models, fields, api

class gmpslittingwaving(models.Model):
    _name = "gmp.slitting.waving"
    _description = "Cán bột"
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
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    slitter_id = fields.Char(string="Mã số dao cắt")
    noodle_diameter = fields.Float(string="Đường kính sợi mì (mm)")
    slitter_speed = fields.Float(string="Vận tốc dao cắt (m/s)")
    noodle_speed = fields.Float(string="Vận tốc sợi mì (m/s) ")
    noodle_density = fields.Char(string="Mật độ sợi/độ đều sợi")
    noodle_surface = fields.Char(string="Bề mặt sợi")
    wave_amplitude = fields.Char(string="Biên độ sóng")
    
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

    # --- CÁC HÀM XỬ LÝ LOGIC ---

    @api.depends('productionplan_id')
    def _compute_productionplanfactory(self):
        for record in self:
            if record.productionplan_id:
                record.productionplanfactory = record.productionplan_id.u_factory
            else:
                record.productionplanfactory = False
   
    @api.onchange('search_docnum')
    def _onchange_search_docnum(self):
        """Tìm kế hoạch sản xuất dựa trên số DocNum nhập vào"""
        if self.search_docnum:
            try:
                docnum_val = int(self.search_docnum)
                plan = self.env['base.daily.production.plan'].search([
                    ('docnum', '=', docnum_val)
                ], limit=1)
                if plan:
                    self.productionplan_id = plan.id
            except ValueError:
                pass
