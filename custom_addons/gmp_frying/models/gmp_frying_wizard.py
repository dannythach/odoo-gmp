from odoo import models, fields, api

class GmpFryingWizard(models.TransientModel):
    _name = "gmp.frying.wizard"
    _description = "Chi tiết (Lines)"

    header_id = fields.Many2one('gmp.frying', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.frying.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_frying_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_frying_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)   
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    tempareture = fields.Float(string="Nhiệt độ chiên (C)")
    frying_time = fields.Float(string="Thời gian chiên (P/s)")
    noodle_moisture = fields.Float(string="Độ ẩm vắt mì (%)")
    oil_indices = fields.Float(string="Chỉ số dầu (AV/PV)")
    shortening_color = fields.Selection(
        [
            ("New", "Mới"),
            ("Old", "Cũ"),
        ],
        string="Màu dầu short",
        default="New"
    )

    bht_level = fields.Float(string="Hàm lượng BHT")
    lipid_level = fields.Float(string="Hàm lượng Lipid")

    # Tình trạng BTP sau chiên
    sfp_status = fields.Char(string="Tình trạng BTP")

    # Tình trạng thiết bị
    machine_condition = fields.Char(string="Tình trạng thiết bị")

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
            
            'tempareture': self.tempareture,
            'frying_time': self.frying_time,
            'noodle_moisture': self.noodle_moisture,
            'oil_indices': self.oil_indices,
            'shortening_color': self.shortening_color,
            
            'bht_level': self.bht_level,
            'lipid_level': self.lipid_level,
            
            'sfp_status': self.sfp_status,
            'machine_condition': self.machine_condition,
            
            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.frying.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_frying_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.frying.wizard',
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
            'res_model': 'gmp.frying.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
            }
        }