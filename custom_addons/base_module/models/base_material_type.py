from odoo import models, fields

class MaterialType(models.Model):
    _name = 'base.material.type'
    _description = 'Material type'
    _auto = True
    _rec_name = 'name'
    # _table = 'comi_get_material_result'
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code must be unique!')
    ]

    code = fields.Char(string="Code", size=20, required=True)
    name = fields.Char(string="Name", size=254)
