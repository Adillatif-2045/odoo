from odoo import fields, models


class EstatePropertiesTag(models.Model):
    _name = "estate.property.tag"

    _description = "Model_3 for Real-Estate Properties"
    name = fields.Char(required=True)

    _sql_constraints = [('unique_tag_name', 'unique (name)','Tag name should be unique.')]
