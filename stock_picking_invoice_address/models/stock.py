# -*- coding: utf-8 -*-

##############################################################################
#
# Invoice Address on stock picking - field
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

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string='Invoice Address',
        compute='_compute_partner_invoice_id',
    )

    # Computed field, rather than related, so easier to override
    @api.one
    @api.depends('sale_id.partner_invoice_id')
    def _compute_partner_invoice_id(self):
        sale = self.sale_id
        self.partner_invoice_id = sale and sale.partner_invoice_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
