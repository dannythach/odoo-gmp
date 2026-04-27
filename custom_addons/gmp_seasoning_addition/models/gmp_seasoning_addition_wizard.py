from odoo import models, fields, api

class GmpSeasoningAdditionWizard(models.TransientModel):
    _name = "gmp.seasoning.addition.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.seasoning.addition', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.seasoning.addition.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_seasoning_addition_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_seasoning_addition_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    seasoning_type = fields.Many2one('base.seasoning.type', string="Loại gói gia vị", required=True)
    seasoning_weight = fields.Selection(
        [
            ("Pass", "Đạt"),
            ("Fail", "Không đạt"),
        ],
        string="Trọng lượng gói gia vị",
        default="Pass"
    )

    deviation = fields.Float(string="Sai lệch (g)")
    quality_of_seasoning = fields.Char(string="Tình trạng chất lượng GGV")
    condition_of_packaging_equipment = fields.Char(string="Tình trạng Bao bì & TB bỏ GGV")
    printed_info = fields.Char(string="Thông tin in trên bao bì GGV")

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
            
            'seasoning_type': self.seasoning_type.id,
            'seasoning_weight': self.seasoning_weight,
            
            'deviation': self.deviation,
            'quality_of_seasoning': self.quality_of_seasoning,
            'condition_of_packaging_equipment': self.condition_of_packaging_equipment,
            'printed_info': self.printed_info,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.seasoning.addition.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_seasoning_addition_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.seasoning.addition.wizard',
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
            'res_model': 'gmp.seasoning.addition.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }