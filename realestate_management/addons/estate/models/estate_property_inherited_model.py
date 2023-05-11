from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'salesman_id', string='Real Estate Management',
                                   domain="[('salesman_id', '=', self.id)]")
