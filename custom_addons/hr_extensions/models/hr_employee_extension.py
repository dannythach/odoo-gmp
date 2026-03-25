from odoo import models, fields

class HrEmployeeExtension(models.Model):
    _inherit = 'hr.employee' # Kế thừa mô hình hr.employee

    PIT_Code = fields.Char(string='Mã số thuế TNCN', help='PIT Code')
    
    dependent_count = fields.Integer(string="Số người phụ thuộc")
    dependent_name = fields.Char(string="Tên người phụ thuộc")
    dependent_note = fields.Text(string="Ghi chú")