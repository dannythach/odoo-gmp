from odoo import models, fields

class SeasoningType(models.Model):
    _name = 'base.seasoning.type'
    _description = 'Seasoning Type'
    _auto = True
    _rec_name = 'name'
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code must be unique!')
    ]

    code = fields.Char(string="Code", size=20, required=True)
    name = fields.Char(string="Name", size=254)
