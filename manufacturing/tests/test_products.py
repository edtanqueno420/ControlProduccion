# manufacturing/tests/test_products.py
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .helpers import create_user, create_admin, auth_client, create_product


class ProductPermissionTests(TestCase):

    def setUp(self):
        self.user    = create_user('frank')
        self.admin   = create_admin()
        self.product = create_product()

    def test_authenticated_can_list(self):
        resp = auth_client(self.user).get('/api/products/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)

    def test_unauthenticated_returns_401(self):
        resp = APIClient().get('/api/products/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/products/', {
            'codigo_sku': 'SKU-002', 'nombre': 'Test',
            'tipo': 'RAW_MATERIAL', 'stock_actual': 10,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.admin).post('/api/products/', {
            'codigo_sku': 'SKU-002', 'nombre': 'New Material',
            'tipo': 'RAW_MATERIAL', 'stock_actual': 10,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class ProductFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('gina'))
        create_product('SKU-001', 'Raw Mat',   'RAW_MATERIAL',   stock_actual=50)
        create_product('SKU-002', 'In Proc',   'IN_PROCESS',     stock_actual=0)
        create_product('SKU-003', 'Finished',  'FINISHED_GOOD',  stock_actual=10, activo=False)

    def test_filter_by_tipo(self):
        resp = self.client.get('/api/products/?tipo=RAW_MATERIAL')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_min_stock(self):
        resp = self.client.get('/api/products/?stock_min=1')
        names = [p['nombre'] for p in resp.data['results']]
        self.assertIn('Raw Mat', names)
        self.assertNotIn('In Proc', names)

    def test_search_by_nombre(self):
        resp = self.client.get('/api/products/?search=Raw')
        self.assertEqual(resp.data['count'], 1)

    def test_available_is_public(self):
        resp = APIClient().get('/api/products/available/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ProductActionTests(TestCase):

    def setUp(self):
        self.admin   = create_admin()
        self.user    = create_user('henry')
        self.product = create_product(stock_actual=10)

    def test_restock_adds_stock(self):
        resp = auth_client(self.admin).post(
            f'/api/products/{self.product.id}/restock/',
            {'quantity': 5}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['new_stock'], 15)

    def test_restock_regular_user_returns_403(self):
        resp = auth_client(self.user).post(
            f'/api/products/{self.product.id}/restock/',
            {'quantity': 5}
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_restock_invalid_quantity(self):
        resp = auth_client(self.admin).post(
            f'/api/products/{self.product.id}/restock/',
            {'quantity': -1}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stats_returns_expected_fields(self):
        resp = auth_client(self.user).get('/api/products/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_active', 'total_stock', 'out_of_stock']:
            self.assertIn(field, resp.data)
