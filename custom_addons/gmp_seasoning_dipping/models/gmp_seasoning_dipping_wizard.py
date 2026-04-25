from odoo import models, fields, api

class GmpSeasoningDippingWizard(models.TransientModel):
    _name = "gmp.seasoning.dipping.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.seasoning.dipping', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.seasoning.dipping', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_seasoning_dipping_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_seasoning_dipping_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    noodle_length = fields.Float(string="Chiều dài sợi mì (cm)")
    standard_weight = fields.Float(string="KL/TL quy định (g)")
    actual_weight = fields.Float(string="KL/ TL đo (g)")
    cutting_speed = fields.Float(string="Tốc độ dao cắt (lần/p)")
    conveyor_speed = fields.Float(string="Vận tốc băng tải")
    post_cutting_status = fields.Char(string="Tình trạng vắt mì sau cắt định lượng")

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
            
            'noodle_length': self.noodle_length,
            'standard_weight': self.standard_weight,
            'actual_weight': self.actual_weight,
            'cutting_speed': self.cutting_speed,
            'conveyor_speed': self.conveyor_speed,
            'post_cutting_status': self.post_cutting_status,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.seasoning.dipping.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_seasoning_dipping_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.seasoning.dipping.wizard',
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
            'res_model': 'gmp.seasoning.dipping.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }