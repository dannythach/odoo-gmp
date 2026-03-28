from odoo import models, fields

class DailyProductionPlanDetail(models.Model):
    _name = 'base.daily.production.plan.detail'
    _description = 'Daily Production Plan Detail'
    _auto = True
    _rec_name = 'proplanentry'
    # _table = 'comi_get_material_result'

    _sql_constraints = [
        ('unique_proplanentry', 'unique(proplanentry)', 'Pro Plan Entry must be unique!')
    ]

    proplanentry = fields.Char(string="Pro Plan Entry", size=10,required=True)
    docentry = fields.Integer(string="Doc Entry")
    lineid = fields.Integer(string="Line ID")

    u_itemcode = fields.Char(string="Item Code", size=50)
    u_dscription = fields.Char(string="Item Description", size=254)

    u_quantity = fields.Float(string="Quantity", digits=(19, 6))
    u_uom = fields.Integer(string="UOM")

    u_factor = fields.Float(string="Factor", digits=(19, 6))
    u_quantitypcs = fields.Float(string="Quantity PCS", digits=(19, 6))
    u_line = fields.Char(string="Production Line", size=20)
    u_remarks = fields.Char(string="Remarks", size=500)
    u_shift = fields.Char(string="Shift", size=2)
    u_oriline = fields.Char(string="Production Original Line", size=20)
    u_btp = fields.Char(string="BTP", size=50)
    u_productiontype = fields.Char(string="Production Type", size=1)
    u_machines = fields.Char(string="Machines", size=50)
    updatedate = fields.Datetime(string="Update Date")
    u_fromts = fields.Integer(string="From TS")
    u_tots = fields.Integer(string="To TS")


