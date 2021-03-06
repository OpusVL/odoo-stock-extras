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


{
    'name': 'Invoice Address on stock picking - Field',
    'version': '0.1',
    'author': 'OpusVL',
    'website': 'http://opusvl.com/',
    'summary': 'Add field partner_invoice_id to stock.picking, computed from sale order.',
    
    'category': 'Warehouse',
    
    'description': """Add field partner_invoice_id to stock.picking.

    The field is pulled directly off the sale order that generated the picking.
    """,
    'images': [
    ],
    'depends': [
        'base',
        'sale_stock',
    ],
    'data': [
        'views/stock_picking.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
