# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class service_mobile(models.Model):
#     _name = 'service_mobile.service_mobile'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class sale_order(models.Model):
    _inherit = "sale.order"

    prio = fields.Boolean(string="Priority", default=False)

    @api.one
    def set_template(self, template_id):
        self.sale_order_template_id = template_id
        self._onchange_eval('sale_order_template_id',"1",{})
        self._onchange_eval('partner_id',"1",{})