# manufacturing/tests/test_production_orders.py
from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user, create_admin, auth_client,
    create_product, create_finished_product,
    create_bom, create_bom_detail,
    create_work_center,
    create_production_order,
)
from manufacturing.models import ProductionOrder, InventoryMovement, Product


class ProductionOrderCRUDTests(TestCase):

    def setUp(self):
        self.user    = create_user('ivan')
        self.admin   = create_admin()
        self.client  = auth_client(self.user)
        self.fg      = create_finished_product('SKU-FG-001', 'Widget', stock_actual=0)
        self.wc      = create_work_center('WC-001', 'Press Machine')
        self.mp      = create_product(
            'SKU-MP-001', 'Steel', 'RAW_MATERIAL', stock_actual=100
        )

    def test_create_order(self):
        resp = self.client.post('/api/production-orders/', {
            'codigo_orden': 'PO-001',
            'producto': self.fg.id,
            'cantidad_a_producir': 10,
            'centro_trabajo': self.wc.id,
            'prioridad': 'HIGH',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['estado'], 'DRAFT')

    def test_add_item_to_order_as_regular_user(self):
        order = create_production_order(
            codigo_orden='PO-001', producto=self.fg,
            cantidad_a_producir=10, usuario_responsable=self.user,
            centro_trabajo=self.wc,
        )
        resp = self.client.get(f'/api/production-orders/{order.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['codigo_orden'], 'PO-001')

    def test_user_cannot_see_other_users_order(self):
        user2 = create_user('kevin')
        order = create_production_order(
            codigo_orden='PO-002', producto=self.fg,
            usuario_responsable=self.user, centro_trabajo=self.wc,
        )
        resp = auth_client(user2).get(f'/api/production-orders/{order.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_see_any_order(self):
        order = create_production_order(
            codigo_orden='PO-003', producto=self.fg,
            usuario_responsable=self.user, centro_trabajo=self.wc,
        )
        resp = auth_client(self.admin).get(f'/api/production-orders/{order.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ProductionOrderWorkflowTests(TestCase):

    def setUp(self):
        self.admin   = create_admin()
        self.user    = create_user('operator')
        self.client  = auth_client(self.admin)
        self.fg      = create_finished_product('SKU-FG-001', 'Widget', stock_actual=0)
        self.wc      = create_work_center('WC-001', 'Press Machine')
        self.mp      = create_product(
            'SKU-MP-001', 'Steel', 'RAW_MATERIAL', stock_actual=100
        )
        # BOM: 1 Widget = 2 Steel + 10% waste = 2.2 Steel per unit
        self.bom     = create_bom(self.fg)
        self.bom_det = create_bom_detail(
            self.bom, self.mp,
            cantidad_requerida=2, desperdicio_porcentaje=10,
        )
        self.order   = create_production_order(
            codigo_orden='PO-001', producto=self.fg,
            cantidad_a_producir=10, usuario_responsable=self.user,
            centro_trabajo=self.wc,
        )

    def test_start_order_validates_stock(self):
        """10 units x 2.2 = 22 Steel needed, we have 100 — should pass."""
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/start/'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['estado'], 'IN_PROGRESS')

    def test_start_order_insufficient_stock(self):
        """Set steel stock to 10 — not enough for 22 needed."""
        self.mp.stock_actual = 10
        self.mp.save()
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/start/'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient', str(resp.data))

    def test_complete_order_consumes_materials_and_inputs_fg(self):
        # First start
        self.client.post(f'/api/production-orders/{self.order.id}/start/')
        # Then complete
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/complete/'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['estado'], 'FINISHED')

        # Check: Steel consumed (10 * 2.2 = 22 consumed, 100 - 22 = 78)
        self.mp.refresh_from_db()
        self.assertEqual(self.mp.stock_actual, 78)

        # Check: FG produced (0 + 10 = 10)
        self.fg.refresh_from_db()
        self.assertEqual(self.fg.stock_actual, 10)

        # Check: Inventory movements created
        movs = InventoryMovement.objects.filter(orden_produccion=self.order)
        self.assertEqual(movs.count(), 2)  # 1 consumption + 1 input

    def test_work_center_exclusivity(self):
        """Cannot have 2 IN_PROGRESS orders on same work center."""
        self.client.post(f'/api/production-orders/{self.order.id}/start/')

        order2 = create_production_order(
            codigo_orden='PO-002', producto=self.fg,
            cantidad_a_producir=5, usuario_responsable=self.user,
            centro_trabajo=self.wc,
        )
        resp = self.client.post(
            f'/api/production-orders/{order2.id}/start/'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already has an order', str(resp.data))

    def test_pause_and_resume(self):
        self.client.post(f'/api/production-orders/{self.order.id}/start/')
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/pause/'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['estado'], 'PAUSED')

    def test_cancel_order(self):
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/cancel/'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['estado'], 'CANCELLED')

    def test_cannot_complete_draft_order(self):
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/complete/'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_start_already_started_order(self):
        self.client.post(f'/api/production-orders/{self.order.id}/start/')
        resp = self.client.post(
            f'/api/production-orders/{self.order.id}/start/'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ProductionOrderStatsTests(TestCase):

    def setUp(self):
        self.admin  = create_admin()
        self.client = auth_client(self.admin)
        self.user   = create_user('laura')
        self.fg     = create_finished_product('SKU-FG-001', 'Widget')
        self.wc     = create_work_center('WC-001', 'Press')
        create_production_order('PO-001', self.fg, 10, 'DRAFT', 'LOW', self.user, self.wc)
        create_production_order('PO-002', self.fg, 20, 'IN_PROGRESS', 'HIGH', self.user, self.wc)

    def test_stats_staff_only(self):
        resp = self.client.get('/api/production-orders/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_orders', 'by_status', 'by_priority']:
            self.assertIn(field, resp.data)

    def test_stats_regular_user_returns_403(self):
        resp = auth_client(create_user('mario')).get('/api/production-orders/stats/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
