# manufacturing/tests/test_work_centers.py
from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_admin, auth_client, create_work_center


class WorkCenterPermissionTests(TestCase):

    def setUp(self):
        self.user   = create_user('eve')
        self.admin  = create_admin()
        self.center = create_work_center()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/work-centers/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/work-centers/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/work-centers/', {
            'codigo': 'WC-002', 'nombre_maquina': 'Test Machine'
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.admin).post('/api/work-centers/', {
            'codigo': 'WC-002', 'nombre_maquina': 'New Machine'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class WorkCenterFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        create_work_center('WC-001', 'Machine 1', estado='ACTIVE')
        create_work_center('WC-002', 'Machine 2', estado='MAINTENANCE')

    def test_filter_by_estado(self):
        resp = self.client.get('/api/work-centers/?estado=MAINTENANCE')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre_maquina'], 'Machine 2')

    def test_search_by_codigo(self):
        resp = self.client.get('/api/work-centers/?search=WC-001')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/work-centers/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'active', 'maintenance', 'inactive', 'detail']:
            self.assertIn(field, resp.data)
