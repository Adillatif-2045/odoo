from odoo import api, fields, models
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError


class EstateProperties(models.Model):
    _name = "estate.property"

    _description = "Model for Real-Estate Properties"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    status = fields.Char()

    data_availability = fields.Date(copy=False, string='Data Availability',
                                    default=lambda self: (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, compute="_compute_selling_price")
    _sql_constraints = [('unique_type_name', 'unique (name)', 'Property Type name should be unique.'),
                        ('check_selling_price', 'check (selling_price > 0)',
                         'Selling Price should be positive and greater than 0.'),
                        ('check_expected_price', 'check (expected_price > 0)',
                         'Expected Price should be Positive and bigger than 0.')
                        ]

    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string="Direction",
                                          selection=[('West', 'west'), ('North', 'north'), ('South', 'south'),
                                                     ('East', 'east')])
    state = fields.Selection(copy=False, required=True, default='New', string="State",
                             selection=[('New', 'new'), ('Offer Received', 'offer received'),
                                        ('Offer Accepted', 'offer accepted'), ('Sold', 'sold'),
                                        ('Canceled', 'canceled')])

    total_area = fields.Integer(compute="_compute_total_area")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    salesman_id = fields.Many2one('res.users', string="Salesman", index=True,
                                  default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string="Buyer", index=True,
                               default=lambda self: self.env.company.id)
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Property Offer")

    best_offer = fields.Float(compute='_compute_best_offer')

    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                max_offer = max(record.offer_ids.mapped('price'))
                record.best_offer = max_offer
            else:
                record.best_offer = False

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'North'
        else:
            self.garden_area = False
            self.garden_orientation = False

    def action_sold(self):
        for record in self:

            if record.status == 'canceled':
                raise UserError("Canceled properties cannot be sold.")
            else:
                record.status = 'sold'

    def action_cancel(self):
        if self.status == 'sold':
            raise UserError("Sold properties cannot be Canceled.")
        self.status = 'canceled'

    @api.depends('offer_ids')
    def _compute_selling_price(self):
        accepted_offers = self.offer_ids.filtered(lambda o: o.status == 'Accepted')
        if accepted_offers:
            self.selling_price = sum(accepted_offers.mapped('price'))

            self.buyer_id = accepted_offers[0].partner_id.id
        else:

            self.selling_price = False
            self.buyer_id = False

    @api.constrains('offer_ids')
    def _check_best_offer(self):
        for record in self:
            best_offer = record.offer_ids.filtered(lambda o: o.price < (record.expected_price * 0.9))
            if best_offer:
                raise ValidationError("Selling Price should be greater than 90% of expected price")

            else:
                record.selling_price = record.best_offer
