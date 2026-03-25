from odoo import models, fields, api
from odoo.osv import expression

class GmpOitm(models.Model):
    _name = "gmp.oitm"
    _description = "Item master data"
    _rec_name = "display_name" # Đổi từ itemcode sang display_name
    _order = "id desc"
    _sql_constraints = [
        ('itemcode_unique', 'unique(itemcode)', 'Mã NPL phải là duy nhất!')
    ]

    itemcode = fields.Char(string="Mã NPL", required=True)
    itemname = fields.Char(string="Tên NPL", required=True)
    frgnname = fields.Char(string="Tên nước ngoài")
    itmsgrpcod = fields.Integer(string="Nhóm hàng")
    iuomcode = fields.Char(string="ĐVT tồn kho (code)")
    iuomname = fields.Char(string="ĐVT tồn kho (name)")
    createdate = fields.Datetime(string="Ngày tạo")
    updatedate = fields.Datetime(string="Ngày cập nhật")
    updatets = fields.Integer(string="Mã thời gian cập nhật")

    # Chỉ cần dùng hàm này để định nghĩa tên hiển thị
    @api.depends('itemcode', 'itemname', 'iuomname', 'iuomcode')
    def _compute_display_name(self):
        for rec in self:
            name = f"[{rec.itemcode}] {rec.itemname or ''}"
            uom = rec.iuomname or rec.iuomcode
            if uom:
                name += f" ({uom})"
            rec.display_name = name

    # Dùng _name_search (chuẩn Odoo mới) để hỗ trợ tìm kiếm khi gõ mã hoặc tên
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            name_domain = expression.OR([
                [('itemcode', operator, name)],
                [('itemname', operator, name)]
            ])
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)