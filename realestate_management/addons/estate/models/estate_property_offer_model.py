from datetime import timedelta, datetime
from odoo import api, fields, models


class EstatePropertiesOffer(models.Model):
    _name = "estate.property.offer"

    _description = "Model_4 for Real-Estate Properties"

    price = fields.Float()
    status = fields.Selection(copy=False, selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')])
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete="cascade")
    validity = fields.Integer(default=7)
    create_date = fields.Datetime(default=fields.Datetime.now)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:

            if record.date_deadline and record.create_date:
                deadline_datetime = datetime.combine(record.date_deadline, datetime.min.time())
                create_datetime = datetime.combine(record.create_date, datetime.min.time())
                record.validity = (deadline_datetime - create_datetime).days

    def action_tick(self):

        self.status = "Accepted"

    def action_cross(self):

        self.status = "Refused"

    _sql_constraints = [('check_price', 'check (price>0)', 'Price should be positive and greater than 0.')]


