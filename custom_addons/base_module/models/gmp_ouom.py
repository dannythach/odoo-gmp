from odoo import models, fields, api
from odoo.osv import expression

class GmpOuom(models.Model):
    _name = "gmp.ouom"
    _description = "Unit of measure"
    # Quan trọng: Gán display_name làm rec_name để Odoo ưu tiên dùng kết quả của hàm compute
    _rec_name = "display_name" 
    _order = "id desc"
    _sql_constraints = [
        ('uomcode_unique', 'unique(uomcode)', 'UOM code must be unique!')
    ]

    uomcode = fields.Char(string="Mã ký hiệu ĐVT", required=True)
    uomname = fields.Char(string="Tên ĐVT", required=True)
    locked = fields.Char(string="Khóa")
    updatedate = fields.Datetime(string="Ngày cập nhật")
    createdate = fields.Datetime(string="Ngày tạo")
    u_uomcode = fields.Char(string="Mã ĐVT (UDF)")

    @api.depends('uomcode', 'uomname')
    def _compute_display_name(self):
        for rec in self:
            # Format: [Mã] - [Tên]
            name = rec.uomcode or ''
            if rec.uomname:
                name = f"{name} - {rec.uomname}"
            rec.display_name = name

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            # Cho phép tìm kiếm bằng cả mã hoặc tên trên điện thoại
            name_domain = expression.OR([
                [('uomcode', operator, name)],
                [('uomname', operator, name)]
            ])
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)