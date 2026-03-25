from odoo import models, fields, api
from odoo.osv import expression

class DailyProductionPlan(models.Model):
    _name = 'base.daily.production.plan'
    _description = 'Daily Production Plan'
    _auto = True
    # Quan trọng: Dùng display_name để hiển thị nội dung tùy chỉnh khi xổ chọn
    _rec_name = 'display_name' 
    # Sắp xếp docnum giảm dần (số lớn nhất/mới nhất nằm trên cùng)
    _order = 'docnum desc'

    _sql_constraints = [
        ('unique_docentry', 'unique(docentry)', 'DocEntry must be unique!')
    ]

    docentry = fields.Integer(string="Doc Entry", required=True)
    docnum = fields.Integer(string="DocNum")

    canceled = fields.Char(string="Canceled", size=1)
    status = fields.Char(string="Status", size=1)

    createdate = fields.Datetime(string="Create Date")
    createtime = fields.Integer(string="Create Time")

    updatedate = fields.Datetime(string="Update Date")
    updatetime = fields.Integer(string="Update Time")
    
    remark = fields.Char(string="Remark", size=500)
    u_docdate = fields.Datetime(string="Doc Date")
    u_factory = fields.Char(string="Factory", size=2)
    u_fromwhs = fields.Char(string="From Warehouse", size=20)
    u_towhs = fields.Char(string="To Warehouse", size=20)

    # Hàm tạo chuỗi hiển thị: "docnum - remark"
    @api.depends('docnum', 'remark')
    def _compute_display_name(self):
        for rec in self:
            name = str(rec.docnum) if rec.docnum else ""
            if rec.remark:
                name = f"{name} - {rec.remark}"
            rec.display_name = name

    # Hỗ trợ tìm kiếm nhanh bằng cả số DocNum hoặc nội dung Remark
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            name_domain = expression.OR([
                [('docnum', operator, name)],
                [('remark', operator, name)]
            ])
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)