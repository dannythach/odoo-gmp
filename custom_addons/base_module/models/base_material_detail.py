from odoo import models, fields

class MaterialDetail(models.Model):
    _name = 'base.material.detail'
    _description = 'SAP Material Detail - Get BOM Quantity'
    _auto = True
    _rec_name = 'materialname'
    # _table = 'comi_get_material_result'

    _sql_constraints = [
        ('unique_docentry', 'unique(docentry)', 'DocEntry must be unique!')
    ]

    docentry = fields.Integer(string="Doc Entry", required=True)
    docnum = fields.Integer(string="DocNum")
    groupno = fields.Integer(string="Group No")

    itmsgrpnam = fields.Char(string="Item Group", size=100)

    materialcode = fields.Char(string="Material Code", size=50)
    materialname = fields.Char(string="Material Name", size=200)

    onhand = fields.Float(string="On Hand", digits=(19,6))
    materialqty = fields.Float(string="Material Qty", digits=(19,6))
    actualqty = fields.Float(string="Actual Qty", digits=(19,6))

    remark = fields.Char(string="Remark", size=500)

    uomentry = fields.Integer(string="UOM Entry")
    uomname = fields.Char(string="UOM Name", size=100)

    fromwhs = fields.Char(string="From Warehouse", size=20)
    towhs = fields.Char(string="To Warehouse", size=20)

    createdate = fields.Datetime(string="Create Date")

    createts = fields.Integer(string="Create TS")
    fromts = fields.Integer(string="From TS")
    tots = fields.Integer(string="To TS")

