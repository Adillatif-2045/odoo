from odoo import fields, models


class EstatePropertiesType(models.Model):
    _name = "estate.property.type"

    _description = "Model_2 for Real-Estate Properties"

    property_type_id = fields.Many2one('estate.property', string="Property Type")
    name = fields.Char(required=True)
