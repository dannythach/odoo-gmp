from odoo import models, fields, api

class GmpSeasoningDippingWizard(models.TransientModel):
    _name = "gmp.seasoning.dipping.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.seasoning.dipping', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.seasoning.dipping.line', string="Dòng đang sửa")

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
    
    equipment_code = fields.Char(string="Mã số thiết bị")
    soup_temperature = fields.Float(string="Nhiệt độ nước lèo (C)")
    dipping_time = fields.Float(string="Thời gian nhúng (s)")
    soup_rate = fields.Float(string="Lưu lượng nước lèo (ml/vắt)")
    noodle_status = fields.Char(string="Tình trạng vắt sau nhúng/phun")

     # Tình trạng bảo quản sau cân - định lượng
    cip = fields.Selection(
        [
            ("Pass", "C"),
            ("Fail", "K"),
        ],
        string="Tình trạng vệ sinh tại chỗ cho hệ thống kín",
        default="Pass"
    )

    # Nhân diện sau cân - định lượng
    cop = fields.Selection(
        [
            ("Pass", "C"),
            ("Fail", "K"),
        ],
        string="Tình trạng tháo rời ra để vệ sinh (dao, khay, dụng cụ…)",
        default="Pass"
    )

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
            
            'equipment_code': self.equipment_code,
            'soup_temperature': self.soup_temperature,
            'dipping_time': self.dipping_time,
            'soup_rate': self.soup_rate,
            'noodle_status': self.noodle_status,
            
            'cip': self.cip,
            'cop': self.cop,
            
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