from odoo import models, fields, api

class GmpMetalDetectionWizard(models.TransientModel):
    _name = "gmp.metal.detection.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.metal.detection', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.metal.detection.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_metal_detection_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_metal_detection_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")

    machine_id = fields.Char(string="Thiết bị dò kim loại (Mã số)")
    machine_type = fields.Many2one('base.machine.type', string="Loại máy", required=True)
    fe_type = fields.Selection(
        [
            ("Pass", "C"),
            ("Fail", "K"),
        ],
        string="Fe (1mm)",
        default="Pass"
    )
    nonfe_type = fields.Selection(
        [
            ("Pass", "C"),
            ("Fail", "K"),
        ],
        string="Non-Fe (1.5mm)",
        default="Pass"
    )
    sus_type = fields.Selection(
        [
            ("Pass", "C"),
            ("Fail", "K"),
        ],
        string="Sus (2.0mm)",
        default="Pass"
    )
    quantity_of_products_scanned = fields.Float(string="Số lượng sản phẩm dò")
    quantity_of_products_detected = fields.Float(string="Số lượng sản phẩm phát hiện")
    fe_detected = fields.Float(string="Số lượng sản phẩm phát hiện Fe")
    nonfe_detected = fields.Float(string="Số lượng sản phẩm phát hiện Non-Fe")
    sus_detected = fields.Float(string="Số lượng sản phẩm phát hiện Sus")

    re_scanned = fields.Float(string="Số lượng dò lại")
    isolated = fields.Float(string="Số lượng cô lập & xử lý")
    opened = fields.Float(string="Số lượng mở gói & xử lý")

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
            
            'machine_id': self.machine_id,
            'machine_type': self.machine_type.id,
            'fe_type': self.fe_type,
            'nonfe_type': self.nonfe_type,
            'sus_type': self.sus_type,
            'quantity_of_products_scanned': self.quantity_of_products_scanned,
            'quantity_of_products_detected': self.quantity_of_products_detected,
            'fe_detected': self.fe_detected,
            'nonfe_detected': self.nonfe_detected,
            'sus_detected': self.sus_detected,
            
            're_scanned': self.re_scanned,
            'isolated': self.isolated,
            'opened': self.opened,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.metal.detection.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_metal_detection_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.metal.detection.wizard',
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
            'res_model': 'gmp.metal.detection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }