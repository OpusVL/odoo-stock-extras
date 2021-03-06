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
from openerp.exceptions import AccessError, AccessDenied

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
            company_id=False,
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

    def _setup_create_salesmen(self):
        self._setup_create_stock_user('acme_widgets')
        self._setup_create_stock_user('acme_anvils')

    def _setup_create_stock_user(self, company_slug, manager=False, all_companies=False):
        prefix = 'stock_manager' if manager else 'stock_user'
        stock_user_slug = '{}_{}'.format(prefix, company_slug)
        email = '{}@test.example.org'.format(stock_user_slug)
        company_id = self.companies[company_slug].id
        if all_companies:
            company_ids = [c.id for c in self.companies.values()]
        else:
            company_ids = [company_id]
        groups_edits = [(4, self.ref('stock.group_stock_manager' if manager else 'stock.group_stock_user'), False)]
        self.users[stock_user_slug] = self.env['res.users'].create({
            'company_id': company_id,
            'company_ids': [(6, False, company_ids)],
            'name': 'TEST {}'.format(stock_user_slug),
            'email': email,
            'login': email,
            'groups_id': groups_edits,
        })


    def _setup_make_company(self, name):
        ResCompany = self.env['res.company']
        self.companies[name] = ResCompany.create(dict(
            name='TEST {}'.format(name),
        ))

    
    def _get_product_as(self, product_slug, user_slug):
        return self.products[product_slug].sudo(self.users[user_slug])
    


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


class StockUserAccessTests(RoutesCaseWithAdminCreatedAnvil):
    """Tests what happens when a stock_user looks at route_ids.
    """
    at_install = False
    post_install = True

    def setUp(self):
        super(StockUserAccessTests, self).setUp()
        self._setup_create_salesmen()

        
    def test_anvil_routes_mto_for_anvils_stock_user(self):
        """ACME Anvils stock_user manufactures Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_user_acme_anvils']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Manufacture']))

        
    def test_widgets_stock_user_buys_anvil_to_order(self):
        """ACME Widgets stock_user buys Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_user_acme_widgets']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Buy']))


    def test_widgets_stock_user_cannot_delete_company_routes(self):
        """ACME Widgets stock_user cannot delete company routes"""
        anvil = self._get_product_as('Anvil', 'stock_user_acme_widgets')

        pcris = anvil.sudo().per_company_route_ids
        for pcri in pcris:
            with self.assertRaises(AccessError):
                anvil.write({
                    'per_company_route_ids': [(2, pcri.id, False)],
                })
                

    def test_widgets_stock_user_cannot_add_company_routes(self):
        """Widgets stock_user may not add their own company to routes.
        """
        anvil = self.products['Anvil']
        # Clear the Anvil's company routes
        anvil.write({'per_company_route_ids': [(2, i, False)
                                               for i in anvil.per_company_route_ids.ids]})
        stock_user = self.users['stock_user_acme_widgets']
        
        with self.assertRaises(AccessError):
            anvil.sudo(stock_user).write({
                'per_company_route_ids': [(0, False, {
                    'company_id': stock_user.company_id.id,
                    'route_ids': [(6, False, [self.routes['Buy'].id])],
                })],
            })
            

    def test_widgets_stock_user_cannot_add_routes_for_company(self):
        """Widgets stock_user may not add routes for a company.
        """
        anvil = self.products['Anvil']
        stock_user = self.users['stock_user_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        widgets_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id
        
        with self.assertRaises(AccessError):
            anvil.sudo(stock_user).write({
                'per_company_route_ids': [(1, widgets_pairing_id, {'route_ids': [(4, self.routes['Manufacture'].id, False)]})],
            })


    def test_widgets_stock_user_cannot_remove_routes_from_company(self):
        """Widgets stock_user may not remove routes from company"""
        anvil = self.products['Anvil']
        stock_user = self.users['stock_user_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        widgets_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id

        with self.assertRaises(AccessError):
            anvil.sudo(stock_user).write({
                'per_company_route_ids': [(1, widgets_pairing_id, {'route_ids': [(3, self.routes['Buy'].id, False)]})],
            })



class UniCompanyStockManagerAccessTests(RoutesCaseWithAdminCreatedAnvil):
    """Test what happens when a uni-company stock manager edits per-company routes.
    """

    def setUp(self):
        super(UniCompanyStockManagerAccessTests, self).setUp()
        self._setup_create_stock_user('acme_anvils', manager=True)
        self._setup_create_stock_user('acme_widgets', manager=True)


    def test_anvil_routes_mto_for_anvils_manager(self):
        """ACME Anvils manager manufactures Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_manager_acme_anvils']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Manufacture']))

        
    def test_widgets_manager_buys_anvil_to_order(self):
        """ACME Widgets manager buys Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_manager_acme_widgets']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Buy']))



    def assertRaisesMentioningAccess(self):
        return self.assertRaisesRegexp(Exception, 'Access')
    
    def test_widgets_manager_cannot_delete_other_company_routes(self):
        """ACME Widgets manager cannot delete other company routes"""
        anvil = self._get_product_as('Anvil', 'stock_manager_acme_widgets')
        manager = self.users['stock_manager_acme_widgets']

        pcris = anvil.sudo().per_company_route_ids.filtered(lambda p: p.company_id != manager.company_id)
        for pcri in pcris:
            with self.assertRaisesMentioningAccess():
                anvil.write({
                    'per_company_route_ids': [(2, pcri.id, False)],
                })


    def test_widgets_manager_cannot_add_other_company_routes(self):
        """Widgets manager may not add other company to routes.
        """
        anvil = self.products['Anvil']
        # Clear the Anvil's company routes
        anvil.write({'per_company_route_ids': [(2, i, False)
                                               for i in anvil.per_company_route_ids.ids]})
        manager = self.users['stock_manager_acme_widgets']
        
        with self.assertRaisesMentioningAccess():
            anvil.sudo(manager).write({
                'per_company_route_ids': [(0, False, {
                    'company_id': self.companies['acme_anvils'].id,
                    'route_ids': [(6, False, [self.routes['Buy'].id])],
                })],
            })
            

    def test_widgets_manager_cannot_add_routes_for_other_company(self):
        """Widgets manager may not add routes for another company.
        """
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_anvils = self.companies['acme_anvils']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_anvils).id
        
        with self.assertRaisesMentioningAccess():
            anvil.sudo(manager).write({
                'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(4, self.routes['Manufacture'].id, False)]})],
            })


    def test_widgets_manager_cannot_remove_routes_from_other_company(self):
        """Widgets manager may not remove routes from other company"""
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_anvils = self.companies['acme_anvils']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_anvils).id

        with self.assertRaisesMentioningAccess():
            anvil.sudo(manager).write({
                'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(3, self.routes['Buy'].id, False)]})],
            })


    def test_widgets_manager_may_delete_own_company_routes(self):
        """ACME Widgets manager may delete own company routes"""
        anvil = self._get_product_as('Anvil', 'stock_manager_acme_widgets')
        manager = self.users['stock_manager_acme_widgets']
        pcris = anvil.sudo().per_company_route_ids.filtered(lambda p: p.company_id == manager.company_id)
        
        anvil.write({
            'per_company_route_ids': [(2, pcris.id, False)],
        })


    def test_widgets_manager_may_add_own_company_routes(self):
        """Widgets manager may add own company to routes.
        """
        anvil = self.products['Anvil']
        # Clear the Anvil's company routes
        anvil.write({'per_company_route_ids': [(2, i, False)
                                               for i in anvil.per_company_route_ids.ids]})
        manager = self.users['stock_manager_acme_widgets']
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(0, False, {
                'company_id': self.companies['acme_widgets'].id,
                'route_ids': [(6, False, [self.routes['Buy'].id])],
            })],
        })

            

    def test_widgets_manager_may_add_routes_for_own_company(self):
        """Widgets manager may routes for their own company.
        """
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(4, self.routes['Manufacture'].id, False)]})],
        })



    def test_widgets_manager_may_remove_routes_from_own_company(self):
        """Widgets manager may remove routes from own company"""
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        widgets_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id

        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, widgets_pairing_id, {'route_ids': [(3, self.routes['Buy'].id, False)]})],
        })
    
            
class MultiCompanyWarehouseManagerAccessTests(RoutesCaseWithAdminCreatedAnvil):
    """Test what happens when a multi-company sales manager edits per-company routes.
    """

    def setUp(self):
        super(MultiCompanyWarehouseManagerAccessTests, self).setUp()
        self._setup_create_stock_user('acme_anvils', manager=True, all_companies=True)
        self._setup_create_stock_user('acme_widgets', manager=True, all_companies=True)
        self.widgets = self.companies['acme_widgets']
        self.anvils = self.companies['acme_anvils']


    def test_anvil_routes_mto_for_anvils_manager(self):
        """Multi-company ACME Anvils manager manufactures Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_manager_acme_anvils']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Manufacture']))

        
    def test_widgets_manager_buys_anvil_to_order(self):
        """Multi-company ACME Widgets manager buys Anvils to order
        """
        result = self.products['Anvil'].sudo(self.users['stock_manager_acme_widgets']).route_ids

        self.assertSetEqual(frozenset(result.mapped('name')), frozenset(['Make To Order', 'Buy']))



    def test_widgets_manager_can_delete_other_company_routes(self):
        """Multi-company ACME Widgets manager can delete other company routes"""
        anvil = self._get_product_as('Anvil', 'stock_manager_acme_widgets')
        manager = self.users['stock_manager_acme_widgets']

        pcri = anvil.sudo().per_company_route_ids.filtered(lambda p: p.company_id == self.widgets)
        anvil.write({
            'per_company_route_ids': [(2, pcri.id, False)],
        })


    def test_widgets_manager_can_add_other_company_routes(self):
        """Multi-company Widgets manager may add other company to routes.
        """
        anvil = self.products['Anvil']
        # Clear the Anvil's company routes
        anvil.write({'per_company_route_ids': [(2, i, False)
                                               for i in anvil.per_company_route_ids.ids]})
        manager = self.users['stock_manager_acme_widgets']
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(0, False, {
                'company_id': self.companies['acme_anvils'].id,
                'route_ids': [(6, False, [self.routes['Buy'].id])],
            })],
        })
            

    def test_widgets_manager_can_add_routes_for_other_company(self):
        """Multi-company Widgets manager may add routes for another company.
        """
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_anvils = self.companies['acme_anvils']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_anvils).id
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(4, self.routes['Manufacture'].id, False)]})],
        })


    def test_widgets_manager_can_remove_routes_from_other_company(self):
        """Multi-company Widgets manager may remove routes from other company"""
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_anvils = self.companies['acme_anvils']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_anvils).id

        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(3, self.routes['Buy'].id, False)]})],
        })


    def test_widgets_manager_may_delete_own_company_routes(self):
        """Multi-company ACME Widgets manager may delete own company routes"""
        anvil = self._get_product_as('Anvil', 'stock_manager_acme_widgets')
        manager = self.users['stock_manager_acme_widgets']
        pcris = anvil.sudo().per_company_route_ids.filtered(lambda p: p.company_id == manager.company_id)
        
        anvil.write({
            'per_company_route_ids': [(2, pcris.id, False)],
        })


    def test_widgets_manager_may_add_own_company_routes(self):
        """Multi-company Widgets manager may add own company to routes.
        """
        anvil = self.products['Anvil']
        # Clear the Anvil's company routes
        anvil.write({'per_company_route_ids': [(2, i, False)
                                               for i in anvil.per_company_route_ids.ids]})
        manager = self.users['stock_manager_acme_widgets']
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(0, False, {
                'company_id': self.companies['acme_widgets'].id,
                'route_ids': [(6, False, [self.routes['Buy'].id])],
            })],
        })

            

    def test_widgets_manager_may_add_routes_for_own_company(self):
        """Multi-company Widgets manager may routes for their own company.
        """
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        anvils_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id
        
        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, anvils_pairing_id, {'route_ids': [(4, self.routes['Manufacture'].id, False)]})],
        })



    def test_widgets_manager_may_remove_routes_from_own_company(self):
        """Multi-company Widgets manager may remove routes from own company"""
        anvil = self.products['Anvil']
        manager = self.users['stock_manager_acme_widgets']
        acme_widgets = self.companies['acme_widgets']
        widgets_pairing_id = anvil.per_company_route_ids.filtered(lambda r: r.company_id == acme_widgets).id

        anvil.sudo(manager).write({
            'per_company_route_ids': [(1, widgets_pairing_id, {'route_ids': [(3, self.routes['Buy'].id, False)]})],
        })
    
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
