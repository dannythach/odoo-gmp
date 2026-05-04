from odoo import models, fields, api

class GmpProductCasingWizard(models.TransientModel):
    _name = "gmp.product.casing.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.product.casing', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.product.casing.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_product_casing_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_product_casing_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    specifications = fields.Char(string="Quy cách (gói/thùng)")
    quantity_case = fields.Float(string="Tổng số thùng")
    inspected_cases = fields.Float(string="Số thùng kiểm")
    passed_cases = fields.Float(string="Số thùng đạt")
    rejected_cases = fields.Float(string="Số thùng không đạt")
    defect_type = fields.Char(string="Loại lỗi")

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
            
            'specifications': self.specifications,
            'quantity_case': self.quantity_case,
            'inspected_cases': self.inspected_cases,
            'passed_cases': self.passed_cases,
            'rejected_cases': self.rejected_cases,
            'defect_type': self.defect_type,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.product.casing.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_product_casing_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.product.casing.wizard',
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
            'res_model': 'gmp.product.casing.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }