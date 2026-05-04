from odoo import models, fields, api

class GmpProductPackagingWizard(models.TransientModel):
    _name = "gmp.product.packaging.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.product.packaging', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.product.packaging.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_product_packaging_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_product_packaging_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    packaging_type = fields.Char(string="Loại bao bì (Đúng loại, sạch, còn hạn, Có CO/DoC)")
    cutter_speed = fields.Float(string="Tốc độ dao cắt (nhát/phút)")
    temperature_at_ends = fields.Float(string="Nhiệt độ điện trở 2 đầu gói mì (C)")
    temperature_for_middle = fields.Float(string="Nhiệt độ điện trở dập phần bụng gói mì (C)")
    total_products = fields.Float(string="Tổng số sản phẩm")
    inspected_products = fields.Float(string="Tổng số sản phẩm kiểm")
    passed_products = fields.Float(string="Tổng số sản phẩm đạt")
    defective_products = fields.Float(string="Tổng số sản phẩm lỗi")
    defect_types = fields.Selection(
        [
            ("PR", "Sản phẩm"),
            ("MA", "Thiết bị"),
        ],
        string="Loại lỗi liên quan",
        default="PR"
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
            
            'packaging_type': self.packaging_type,
            'cutter_speed': self.cutter_speed,
            'temperature_at_ends': self.temperature_at_ends,
            'temperature_for_middle': self.temperature_for_middle,
            'total_products': self.total_products,
            'inspected_products': self.inspected_products,
            'passed_products': self.passed_products,
            'defective_products': self.defective_products,
            'defect_types': self.defect_types,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.product.packaging.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_product_packaging_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.product.packaging.wizard',
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
            'res_model': 'gmp.product.packaging.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }