# -*- coding: utf-8 -*-

##############################################################################
#
# Multi-company record rule fixes for stock_account
# Copyright (C) 2017 OpusVL (<https://opusvl.com>)
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
    'name': 'Multi-company record rule fixes for stock_account',
    'version': '0.1',
    'author': 'OpusVL',
    'website': 'https://opusvl.com',
    'summary': 'Fix up the standard multi-company record rules so current stock valuation report works correctly',
    
    'category': 'Technical',
    
    'description': """Fix up the standard multi-company record rules so current stock valuation report works correctly.

    Try installing this if you are experiencing Access Errors reading
    product.product if your users try to access Warehouse -> Inventory Control -> Current Inventory Valuation.
""",
    'images': [
    ],
    'depends': [
        'stock_account',
    ],
    'data': [
        'security/stock_account_security.xml',
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
