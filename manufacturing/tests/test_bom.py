# manufacturing/tests/test_bom.py
from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user, create_admin, auth_client,
    create_product, create_finished_product,
    create_bom, create_bom_detail,
)
from manufacturing.models import BillOfMaterial, BillOfMaterialDetail


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


class BOMDetailTests(TestCase):

    def setUp(self):
        self.admin   = create_admin()
        self.user    = create_user('bom_user')
        self.client  = auth_client(self.admin)
        self.mp1     = create_product('SKU-MP-001', 'Steel Plate', stock_actual=100)
        self.mp2     = create_product('SKU-MP-002', 'Aluminum Sheet', stock_actual=50)
        self.fg      = create_finished_product('SKU-FG-001', 'Metal Box')
        self.bom     = create_bom(self.fg)
        self.other   = create_bom(create_finished_product('SKU-FG-002', 'Plastic Case'))
        self.detail  = create_bom_detail(self.bom, self.mp1, cantidad_requerida=2, desperdicio_porcentaje=10)

    def test_list_details_by_bom(self):
        resp = self.client.get(f'/api/bom-details/?lista_materiales={self.bom.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_list_details_excludes_other_boms(self):
        resp = self.client.get(f'/api/bom-details/?lista_materiales={self.other.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 0)

    def test_create_bom_detail(self):
        resp = self.client.post('/api/bom-details/', {
            'lista_materiales': self.bom.id,
            'materia_prima': self.mp2.id,
            'cantidad_requerida': '5',
            'desperdicio_porcentaje': '15',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BillOfMaterialDetail.objects.count(), 2)
        self.assertEqual(resp.data['materia_prima_nombre'], 'Aluminum Sheet')

    def test_create_requires_lista_materiales(self):
        resp = self.client.post('/api/bom-details/', {
            'materia_prima': self.mp2.id,
            'cantidad_requerida': '3',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_bom_detail(self):
        resp = self.client.put(f'/api/bom-details/{self.detail.id}/', {
            'lista_materiales': self.bom.id,
            'materia_prima': self.mp2.id,
            'cantidad_requerida': '99',
            'desperdicio_porcentaje': '0',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.detail.refresh_from_db()
        self.assertEqual(self.detail.cantidad_requerida, 99)

    def test_delete_bom_detail(self):
        resp = self.client.delete(f'/api/bom-details/{self.detail.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BillOfMaterialDetail.objects.count(), 0)

    def test_regular_user_cannot_create_bom_detail(self):
        resp = auth_client(self.user).post('/api/bom-details/', {
            'lista_materiales': self.bom.id,
            'materia_prima': self.mp1.id,
            'cantidad_requerida': '1',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_read_bom_details(self):
        resp = auth_client(self.user).get(f'/api/bom-details/?lista_materiales={self.bom.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
