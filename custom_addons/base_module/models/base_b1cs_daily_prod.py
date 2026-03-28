from odoo import models, fields, api
from odoo.osv import expression
import werkzeug.urls

class DailyProductionPlan(models.Model):
    _name = 'base.daily.production.plan'
    _description = 'Daily Production Plan'
    _rec_name = 'display_name' 
    _order = 'docnum desc'

    _sql_constraints = [
        ('unique_docentry', 'unique(docentry)', 'DocEntry must be unique!')
    ]

    docentry = fields.Integer(string="Doc Entry", required=True)
    docnum = fields.Integer(string="Kế hoạch sản xuất")
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


    # Link QR để quét - Sử dụng record.id (ID thực như 2611)
    mixing_qr_link = fields.Char(string="Link QR Nhào trộn", compute="_compute_mixing_qr_link")

    @api.depends('docnum', 'remark')
    def _compute_display_name(self):
        for rec in self:
            name = str(rec.docnum) if rec.docnum else ""
            if rec.remark:
                name = f"{name} - {rec.remark}"
            rec.display_name = name

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

    def _compute_mixing_qr_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            # Kiểm tra chính xác XML ID của action
            action = self.env.ref('gmp_material_mixing.action_gmp_material_mixing_create')
            action_id = action.id
        except Exception:
            action_id = False

        for record in self:
            # Kiểm tra record.id là số nguyên dương (đã lưu vào DB)
            if action_id and base_url and isinstance(record.id, int):
                params = {
                    'action': action_id,
                    'active_id': record.id, # Đây là 2611
                }
                query_string = werkzeug.urls.url_encode(params)
                record.mixing_qr_link = f"{base_url}/web#{query_string}"
            else:
                record.mixing_qr_link = False