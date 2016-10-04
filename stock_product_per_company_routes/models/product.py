# -*- coding: utf-8 -*-

##############################################################################
#
# Per-company procurement routes on products
# Copyright (C) 2016 OpusVL (<http://opusvl.com/>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    route_ids = fields.Many2many(
        compute='_compute_route_ids',
        readonly=True,
    )
    
    per_company_route_ids = fields.One2many(
        string='Per-Company Routes',
        comodel_name='product.template.company.routes',
        inverse_name='product_tmpl_id',
    )

    @api.depends('per_company_route_ids')
    @api.one
    def _compute_route_ids(self):
        self.route_ids = self.per_company_route_ids._get_company_routes(self.env.user.company_id)



class ProductTemplateCompanyRoutes(models.Model):
    _name = 'product.template.company.routes'

    _sql_constraints = [
        ('unique_product_tmpl_id_company_id', 'UNIQUE(product_tmpl_id, company_id)',
         'at most one entry is permitted per product company'),
    ]

    product_tmpl_id = fields.Many2one(
        string='Product',
        comodel_name='product.template',
        required=True,
    )

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
    )

    route_ids = fields.Many2many(
        string='Routes',
        comodel_name='stock.location.route',
        required=True,
        domain=[('product_selectable', '=', True)],
    )

    def _get_company_routes(self, company):
        return self.filtered(lambda r: r.company_id == company).mapped('route_ids')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
