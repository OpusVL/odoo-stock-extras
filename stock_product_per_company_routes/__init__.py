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

from . import models
from openerp import SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    _logger.info('In post_init_hook')
    try:
        backup_existing_product_routes(cr)
    finally:
        _logger.info('End of pre_init_hook')

def backup_existing_product_routes(cr):
    _logger.info('Backing up existing product routes table')
    cr.execute("""
    CREATE TABLE stock_product_per_company_existing_product_routes AS SELECT * FROM stock_route_product
    """)


def post_init_hook(cr, registry):
    _logger.info('In post_init_hook')
    try:
        migrate_product_routes(cr, registry)
        drop_backup_routes_table(cr)
    finally:
        _logger.info('End of post_init_hook')

def drop_backup_routes_table(cr):
    _logger.info('Dropping backup routes table')
    cr.execute("""DROP TABLE stock_product_per_company_existing_product_routes""")


def migrate_product_routes(cr, registry):
    _logger.info('Migrating existing product routes into per-company routes model')
    existing_product_routes = get_existing_product_routes(cr)
    uid = SUPERUSER_ID
    product_route_ids = {}
    for (product_id, route_id) in existing_product_routes:
        product_route_ids.setdefault(product_id, [])
        product_route_ids[product_id].append(route_id)
        
    Product = registry['product.template']
    company_ids = registry['res.company'].search(cr, uid, [], context={})
    for (product_id, route_ids) in product_route_ids.items():
        product = Product.browse(cr, uid, product_id, context={})
        product.write({
            'per_company_route_ids': [(0, False, {'company_id': cid,
                                                  'route_ids': [(6, False, product_route_ids[product_id])]}
                                      ) for cid in company_ids]
        })
        
        
def get_existing_product_routes(cr):
    """Return [(product_id, route_id)] from our backup of the product routes relation.
    """
    cr.execute("""
    SELECT product_id, route_id FROM stock_product_per_company_existing_product_routes
    """)
    return cr.fetchall()

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
