# manufacturing/tests/helpers.py
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from manufacturing.models import (
    Profile, Product, BillOfMaterial, BillOfMaterialDetail,
    WorkCenter, ProductionOrder, InventoryMovement,
)


def create_user(username='user', email=None, password='Pass1234!', role='OPERARIO', **kwargs):
    email = email or f'{username}@test.com'
    is_staff = role in ['ADMIN', 'SUPERVISOR']
    user = User.objects.create_user(
        username=username, email=email, password=password,
        is_staff=is_staff, **kwargs
    )
    Profile.objects.create(user=user, role=role)
    return user


def create_admin(username='admin', email=None, password='Admin1234!'):
    return create_user(username=username, email=email, password=password, role='ADMIN')


def create_supervisor(username='supervisor', email=None, password='Admin1234!'):
    return create_user(username=username, email=email, password=password, role='SUPERVISOR')


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def auth_client(user):
    client = APIClient()
    access, _ = get_tokens(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
    return client


def create_product(
    codigo_sku='SKU-001', nombre='Test Product', tipo='RAW_MATERIAL',
    stock_actual=100, activo=True,
):
    return Product.objects.create(
        codigo_sku=codigo_sku, nombre=nombre, tipo=tipo,
        stock_actual=stock_actual, activo=activo,
    )


def create_finished_product(
    codigo_sku='SKU-FG-001', nombre='Finished Good', stock_actual=0,
):
    return create_product(
        codigo_sku=codigo_sku, nombre=nombre,
        tipo='FINISHED_GOOD', stock_actual=stock_actual,
    )


def create_bom(producto_terminado, activa=True, version=1):
    return BillOfMaterial.objects.create(
        producto_terminado=producto_terminado,
        version=version,
        activa=activa,
    )


def create_bom_detail(bom, materia_prima, cantidad_requerida=2, desperdicio_porcentaje=10):
    return BillOfMaterialDetail.objects.create(
        lista_materiales=bom,
        materia_prima=materia_prima,
        cantidad_requerida=cantidad_requerida,
        desperdicio_porcentaje=desperdicio_porcentaje,
    )


def create_work_center(
    codigo='WC-001', nombre_maquina='Machine 1',
    estado='ACTIVE', activo=True,
):
    return WorkCenter.objects.create(
        codigo=codigo, nombre_maquina=nombre_maquina,
        estado=estado, activo=activo,
    )


def create_production_order(
    codigo_orden='PO-001', producto=None, cantidad_a_producir=10,
    estado='DRAFT', prioridad='MEDIUM',
    usuario_responsable=None, centro_trabajo=None,
):
    if producto is None:
        producto = create_finished_product()
    if usuario_responsable is None:
        usuario_responsable = create_user('operator')
    if centro_trabajo is None:
        centro_trabajo = create_work_center()
    return ProductionOrder.objects.create(
        codigo_orden=codigo_orden,
        producto=producto,
        cantidad_a_producir=cantidad_a_producir,
        estado=estado,
        prioridad=prioridad,
        usuario_responsable=usuario_responsable,
        centro_trabajo=centro_trabajo,
    )
