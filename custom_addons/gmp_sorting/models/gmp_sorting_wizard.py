from odoo import models, fields, api

class GmpSortingWizard(models.TransientModel):
    _name = "gmp.sorting.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.sorting', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.sorting.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_sorting_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_sorting_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    number_of_noodle_cakes = fields.Float(string="Tổng số vắt")
    number_of_inspected_cakes = fields.Float(string="Số vắt kiểm")
    number_of_qualified_cakes = fields.Float(string="Số vắt đạt")
    quantity_of_downgraded_cakes = fields.Float(string="Số lượng vắt hạ phẩm cấp")
    substandard_defect_name = fields.Char(string="Tên lỗi thứ phẩm")
    reject_defect_name = fields.Char(string="Tên lỗi phế phẩm")
    reject_rate = fields.Float(string="Tỷ lệ (%)")

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
            
            'number_of_noodle_cakes': self.number_of_noodle_cakes,
            'number_of_inspected_cakes': self.number_of_inspected_cakes,
            'number_of_qualified_cakes': self.number_of_qualified_cakes,
            'quantity_of_downgraded_cakes': self.quantity_of_downgraded_cakes,
            'substandard_defect_name': self.substandard_defect_name,
            'reject_defect_name': self.reject_defect_name,
            'reject_rate': self.reject_rate,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.sorting.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_sorting_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.sorting.wizard',
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
            'res_model': 'gmp.sorting.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }