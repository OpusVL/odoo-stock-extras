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

from openerp.tests import common
from openerp import SUPERUSER_ID

class RoutesCase(common.TransactionCase):
    def setUp(self):
        super(RoutesCase, self).setUp()
        Route = self.env['stock.location.route']
        self.products = {}
        self.routes = {}
        self.users = {}
        self.companies = {}
        
        self.users['admin'] = self.env['res.users'].browse(SUPERUSER_ID)
        self._setup_make_company('acme_widgets')
        self._setup_make_company('acme_anvils')

        self.routes['Make To Order'] = Route.search([('name', '=', 'Make To Order')])
        # The Buy and Manufacture routes are fakes, just copies of Make To Order.
        # Good enough for a white-box unit test.
        self.routes['Buy'] = self.routes['Make To Order'].copy({'name': 'Buy'})
        self.routes['Manufacture'] = self.routes['Make To Order'].copy({'name': 'Manufacture'})
        for r in self.routes.values():
            r.company_id = False

    def setup_create_anvil(self):
        self.products['Anvil'] = self.env['product.template'].create(dict(
            name='TEST Anvil',
            per_company_route_ids=[
                (0, False, {'company_id': self.companies['acme_anvils'].id,
                            'route_ids': [(6, False, [self.routes[name].id
                                                      for name in ['Make To Order',
                                                                   'Manufacture']])]}),
                (0, False, {'company_id': self.companies['acme_widgets'].id,
                            'route_ids': [(6, False, [self.routes[name].id
                                                      for name in ['Make To Order', 'Buy']])]}),
            ],
        ))

    def _setup_make_company(self, name):
        ResCompany = self.env['res.company']
        self.companies[name] = ResCompany.create(dict(
            name='TEST {}'.format(name),
        ))

class RoutesCaseWithAdminCreatedAnvil(RoutesCase):
    def setUp(self):
        super(RoutesCaseWithAdminCreatedAnvil, self).setUp()
        self.setup_create_anvil()


class SetupTests(RoutesCaseWithAdminCreatedAnvil):
    """Sanity checks of the common setup and setup helpers.
    """
    at_install = False
    post_install = True


    def test_setup_make_company(self):
        self._setup_make_company('acme_tunnels')

        result = self.companies['acme_tunnels']

        self.assertEqual(result.name, 'TEST acme_tunnels')


    def test_setup_of_routes(self):
        result = self.routes
        
        self.assertSetEqual(frozenset(r.name for r in result.values()), frozenset(['Make To Order', 'Buy', 'Manufacture']))
        self.assertFalse(any(r.company_id for r in result.values()))


class AdminSwitchingHatsTests(RoutesCaseWithAdminCreatedAnvil):
    """Tests what happens when the Admin user is logged in and is switching hats between companies.
    """
    at_install = False
    post_install = True


    def test_anvil_routes_mto_for_anvils_company(self):
        """ACME Anvils manufactures Anvils to order
        """
        self.users['admin'].company_id = self.companies['acme_anvils']
        
        result = self.products['Anvil'].sudo(self.users['admin']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Manufacture']))

        
    def test_widgets_company_buys_anvil_to_order(self):
        """ACME Widgets buys Anvils to order
        """
        self.users['admin'].company_id = self.companies['acme_widgets']
        
        result = self.products['Anvil'].sudo(self.users['admin']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Buy']))
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
