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

from openerp.osv import osv
from openerp.osv import fields as old_fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    per_company_route_ids = fields.One2many(
        string='Per-Company Routes',
        comodel_name='product.template.company.routes',
        inverse_name='product_tmpl_id',
        help='Maps companies to their ticked routes.  If a company is missing from this table, this is equivalent to having no routes selected.',
    )



class product_template(osv.osv):
    _inherit = 'product.template'

    # Setting the computed via the old API bypasses the cache and the need for @api.depends,
    # and so allows the value of the computed field to depend on context, who is logged in, etc

    _columns = {
        'route_ids': old_fields.function(
            lambda self, *a, **kw: self._calculate_route_ids(*a, **kw),
            relation='stock.location.route',
            store=False,
            method=True,
            type='many2many',
        ),
    }
        
    def _calculate_route_ids(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        products = self.pool['product.template'].browse(cr, uid, ids, context=context)
        for product in products:
            res[product.id] = product.per_company_route_ids._get_company_routes(user.company_id)
        return res



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
