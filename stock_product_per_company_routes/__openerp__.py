# -*- coding: utf-8 -*-

##############################################################################
#
# Per-company procurement rules on products
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
    'name': 'Per-company procurement routes on products',
    'version': '0.1',
    'author': 'OpusVL',
    'website': 'http://opusvl.com/',
    'summary': 'Per-company procurement routes on products',
    
    'category': 'Warehouse',
    
    'description': """Per-company procurement routes on products.


    This adds a new table to the procurements tab of the product form,
    and the original Routes field is made read-only and computed based on the contents of that table.
    
    In order to see the per-company route list you need to be in the group Technical Settings / Show per-company routes on products.

    In order to change the per-company routes you need to be in the group Warehouse / Manager.
""",
    'images': [
    ],
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'views/product.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'pre_init_hook': 'pre_init_hook',
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
