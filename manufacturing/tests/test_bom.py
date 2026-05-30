# manufacturing/tests/test_bom.py
from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user, create_admin, auth_client,
    create_product, create_finished_product,
    create_bom, create_bom_detail,
)
from manufacturing.models import BillOfMaterial


class BOMTests(TestCase):

    def setUp(self):
        self.admin   = create_admin()
        self.user    = create_user('bom_user')
        self.client  = auth_client(self.admin)
        self.mp      = create_product(
            'SKU-MP-001', 'Steel Plate', 'RAW_MATERIAL', stock_actual=100
        )
        self.fg      = create_finished_product(
            'SKU-FG-001', 'Metal Box', stock_actual=0
        )

    def test_create_bom(self):
        resp = self.client.post('/api/bill-of-materials/', {
            'producto_terminado': self.fg.id,
            'version': 1,
            'cantidad_base': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_bom_has_correct_related_name(self):
        bom = create_bom(self.fg)
        self.assertEqual(bom.producto_terminado, self.fg)

    def test_staff_can_create_bom(self):
        resp = auth_client(self.admin).post('/api/bill-of-materials/', {
            'producto_terminado': self.fg.id,
            'version': 1,
            'cantidad_base': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_regular_user_cannot_create_bom(self):
        resp = auth_client(self.user).post('/api/bill-of-materials/', {
            'producto_terminado': self.fg.id,
            'version': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_bom_stats(self):
        create_bom(self.fg)
        resp = self.client.get('/api/bill-of-materials/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'active', 'inactive', 'detail']:
            self.assertIn(field, resp.data)
