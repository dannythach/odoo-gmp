from odoo import models, fields, api

class GmpMoldingAdjustmentWizard(models.TransientModel):
    _name = "gmp.molding.adjustment.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.molding.adjustment', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.molding.adjustment.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_molding_adjustment_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_molding_adjustment_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    adjustment_stick_diameter = fields.Float(string="Đường kính đũa (mm)")
    adjustment_stick_length = fields.Float(string="Chiều dài đũa (mm)")
    distance_stick_mold = fields.Float(string="K/C chỉnh đũa & khuôn (mm)")
    air_flow_rate = fields.Float(string="Hơi khí nén (m³/p)")
    air_pressure = fields.Float(string="Hơi khí nén (bar)")
    fan_speed = fields.Float(string="Vận tốc cánh quạt (v/p)")
    fan_wind_speed = fields.Float(string="Vận tốc gió (m/s)")

    # Tình trạng BTP sau sửa
    sfp_status  = fields.Char(string="Tình trạng BTP sau sửa")

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
            
            'adjustment_stick_diameter': self.adjustment_stick_diameter,
            'adjustment_stick_length': self.adjustment_stick_length,
            'distance_stick_mold': self.distance_stick_mold,
            'air_flow_rate': self.air_flow_rate,
            'air_pressure': self.air_pressure,
            'fan_speed': self.fan_speed,
            'fan_wind_speed': self.fan_wind_speed,
            
            'sfp_status': self.sfp_status,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.molding.adjustment.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_molding_adjustment_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.molding.adjustment.wizard',
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
            'res_model': 'gmp.molding.adjustment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }