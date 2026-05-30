# manufacturing/tests/test_inventory_movements.py
from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_admin, auth_client, create_product


class InventoryMovementTests(TestCase):

    def setUp(self):
        self.user    = create_user('inv_user')
        self.admin   = create_admin()
        self.product = create_product(stock_actual=50)
        self.client  = auth_client(self.admin)

    def test_list_movements_empty(self):
        resp = auth_client(self.user).get('/api/inventory-movements/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)

    def test_adjust_stock_creates_movement(self):
        resp = self.client.post('/api/inventory-movements/adjust/', {
            'producto_id': self.product.id,
            'nueva_cantidad': 100,
            'motivo': 'Inventory correction',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['tipo_movimiento'], 'ADJUSTMENT')
        self.assertEqual(float(resp.data['stock_anterior']), 50)
        self.assertEqual(float(resp.data['stock_nuevo']), 100)

    def test_adjust_stock_updates_product(self):
        self.client.post('/api/inventory-movements/adjust/', {
            'producto_id': self.product.id,
            'nueva_cantidad': 75,
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_actual, 75)

    def test_adjust_stock_regular_user_returns_403(self):
        resp = auth_client(self.user).post('/api/inventory-movements/adjust/', {
            'producto_id': self.product.id,
            'nueva_cantidad': 100,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_missing_fields(self):
        resp = self.client.post('/api/inventory-movements/adjust/', {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adjust_invalid_product(self):
        resp = self.client.post('/api/inventory-movements/adjust/', {
            'producto_id': 9999,
            'nueva_cantidad': 100,
        })
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_stats_returns_expected_fields(self):
        resp = auth_client(self.user).get('/api/inventory-movements/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_movements', 'by_type', 'totals_by_type']:
            self.assertIn(field, resp.data)
