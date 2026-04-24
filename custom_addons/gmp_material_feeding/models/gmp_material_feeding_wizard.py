from odoo import models, fields, api

class GmpMaterialFeedingWizard(models.TransientModel):
    _name = "gmp.material.feeding.wizard"
    _description = "Chi tiết cấp liệu (Lines)"

    header_id = fields.Many2one('gmp.material.feeding', string="Phiếu gốc")
    
    # TRƯỜNG KỸ THUẬT: Để biết đang sửa dòng nào (nếu có)
    line_id = fields.Many2one('gmp.material.feeding.line', string="Dòng đang sửa")

    # Many2many với relation riêng để tránh lỗi Table/Column
    valid_item_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_material_feeding_wizard_item_rel', 
        'wizard_id', 'item_id', 
        string='Sản phẩm hợp lệ'
    )
    valid_material_ids = fields.Many2many(
        'gmp.oitm', 
        'gmp_material_feeding_wizard_material_rel', 
        'wizard_id', 'material_id', 
        string='Nguyên liệu hợp lệ'
    )

    log_datetime = fields.Datetime(string="Thời gian", default=fields.Datetime.now, required=True)

    # Sản phẩm & Nguyên liệu
    # item_id = fields.Many2one('gmp.oitm', string="Sản phẩm", required=True)
    # itemcode = fields.Char(related="item_id.itemcode", readonly=True)
    # fromts = fields.Integer(string="Từ TS", readonly=True)
    # tots = fields.Integer(string="Đến TS", readonly=True)
    
    material_id = fields.Many2one('gmp.oitm', string="Nguyên phụ liệu", required=True)
    materialcode = fields.Char(related="material_id.itemcode", readonly=True)
    materialname = fields.Char(related="material_id.itemname", readonly=True)
    
    uom_id = fields.Many2one('gmp.ouom', string="Đơn vị tính", required=True)
    lot_code = fields.Char(string="Mã lô SX")
    batch_code = fields.Char(string="Mã mẻ")
    
    bom_quantity = fields.Float(string="SL Định mức")
    actual_quantity = fields.Float(string="SL Thực cân", required=True)
    quantity_variance = fields.Float(string="Chênh lệch", readonly=True)
    
    cip = fields.Selection([("Pass", "C"), ("Fail", "K")], string="Tình trạng vệ sinh tại chỗ cho hệ thống kín", default="Pass")
    cop = fields.Selection([("Pass", "C"), ("Fail", "K")], string="Tình trạng tháo rời ra để vệ sinh (dao, khay, dụng cụ…)", default="Pass")
    plan_quantity_status = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Cấp liệu theo lệnh sản xuất", default="Pass")
    bom_quantity_status = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Cấp liệu theo đinh mức/BOM", default="Pass")
    order_quantity_status = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Cấp liệu theo trình tự", default="Pass")
    cleanliness_status = fields.Selection([("Pass", "Sạch"), ("Fail", "Không đạt")], string="Tình trạng vệ sinh ở khu vực cấp liệu", default="Pass")
    operating_status = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Thao tác cấp liệu", default="Pass")
    cross_contamination = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Kiểm soát lây nhiễm chéo", default="Pass")

    result = fields.Selection([("Pass", "Đạt"), ("Fail", "Không đạt")], string="Kết quả", default="Pass")
    operator = fields.Many2one(
        comodel_name="res.users",
        string="Người vận hành",
        default=lambda self: self.env.user
    )
    note = fields.Text(string="Ghi chú")

    @api.onchange('item_id', 'material_id', 'actual_quantity', 'bom_quantity')
    def _onchange_load_data(self):
        plan = self.header_id.productionplan_id
        
        # # 1. LOAD FROMTS, TOTS
        # if plan and self.item_id:
        #     prod_detail = self.env['base.daily.production.plan.detail'].search([
        #         ('docentry', '=', plan.docentry),
        #         ('u_itemcode', '=', self.item_id.itemcode)
        #     ], limit=1, order='id asc')
        #     self.fromts = prod_detail.u_fromts if prod_detail else 0
        #     self.tots = prod_detail.u_tots if prod_detail else 0
        # else:
        #     self.fromts = self.tots = 0 

        # 2. LOAD UOM & BOM
        if self.material_id:
            if self.material_id.iuomcode:
                uom = self.env['gmp.ouom'].search([('uomcode', '=', self.material_id.iuomcode)], limit=1)
                self.uom_id = uom.id if uom else False

            if plan:
                material = self.env['base.material.detail'].search([
                    ('materialcode', '=', self.material_id.itemcode),
                    ('docnum', '=', plan.docnum)
                ], limit=1)
                self.bom_quantity = material.materialqty if material else 0.0
        else:
            self.bom_quantity = 0.0

        # Tính toán chênh lệch
        self.quantity_variance = (self.actual_quantity or 0.0) - (self.bom_quantity or 0.0)

    def action_confirm(self):
        self.ensure_one()
        
        # Chuẩn bị dữ liệu để lưu
        vals = {
            'header_id': self.header_id.id,
            'log_datetime': self.log_datetime,
            # 'item_id': self.item_id.id,
            # 'fromts': self.fromts,
            # 'tots': self.tots,
            'material_id': self.material_id.id,
            'uom_id': self.uom_id.id,
            'lot_code': self.lot_code,
            'batch_code': self.batch_code,
            'bom_quantity': self.bom_quantity,
            'actual_quantity': self.actual_quantity,
            'quantity_variance': self.quantity_variance,
            
            'cip': self.cip,
            'cop': self.cop,
            'plan_quantity_status': self.plan_quantity_status,
            'bom_quantity_status': self.bom_quantity_status,
            'order_quantity_status': self.order_quantity_status,
            'cleanliness_status': self.cleanliness_status,
            'operating_status': self.operating_status,
            'cross_contamination': self.cross_contamination,

            'result': self.result,
            'operator': self.operator.id,
            'note': self.note,
        }

        if self.line_id:
            # NẾU CÓ LINE_ID: Cập nhật dòng hiện tại
            self.line_id.write(vals)
        else:
            # NẾU KHÔNG CÓ LINE_ID: Tạo dòng mới
            self.env['gmp.material.feeding.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_material_feeding_wizard(self):
        self.ensure_one()
        # Nếu là bản ghi mới (chưa có ID thực), Odoo sẽ tự động lưu khi gọi action này 
        # thông qua button type="object"
        
        return {
            'name': 'Thêm dòng nhanh (Mobile)',
            'type': 'ir.actions.act_window',
            'res_model': 'gmp.material.feeding.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.id,
                # 'default_valid_item_ids': self.valid_item_ids.ids,
                'default_valid_material_ids': self.valid_material_ids.ids,
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
            'res_model': 'gmp.material.feeding.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_header_id': self.header_id.id,
                # 'default_valid_item_ids': [(6, 0, self.valid_item_ids.ids)],
                'default_valid_material_ids': [(6, 0, self.valid_material_ids.ids)],
            }
        }