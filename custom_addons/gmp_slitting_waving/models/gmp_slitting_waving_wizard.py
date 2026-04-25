from odoo import models, fields, api

class GmpSlittingWavingWizard(models.TransientModel):
    _name = "gmp.slitting.waving.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.slitting.waving', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.slitting.waving.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_slitting_waving_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_slitting_waving_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

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

    def action_confirm(self):
        self.ensure_one()
        
        # Chuẩn bị dữ liệu để lưu
        vals = {
            'header_id': self.header_id.id,
            'log_datetime': self.log_datetime,
            'lot_code': self.lot_code,
            'batch_code': self.batch_code,
            
            'slitter_id': self.slitter_id,
            'noodle_diameter': self.noodle_diameter,
            'slitter_speed': self.slitter_speed,
            'noodle_speed': self.noodle_speed,
            'noodle_density': self.noodle_density,
            'noodle_surface': self.noodle_surface,
            'wave_amplitude': self.wave_amplitude,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.slitting.waving.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_slitting_waving_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.slitting.waving.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.id,
                'default_line_id': False,
            }
        }

    def action_confirm_and_new(self):
        self.ensure_one()

        # 1. Gọi logic save hiện tại
        self.action_confirm()

        # 2. Reset lại wizard (mở lại form mới)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.slitting.waving.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }