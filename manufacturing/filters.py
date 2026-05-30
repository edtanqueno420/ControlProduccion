# manufacturing/filters.py
import django_filters
from manufacturing.models import Product, BillOfMaterial, WorkCenter, ProductionOrder, InventoryMovement


class ProductFilter(django_filters.FilterSet):
    nombre         = django_filters.CharFilter(lookup_expr='icontains')
    stock_min      = django_filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_max      = django_filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')

    class Meta:
        model  = Product
        fields = ['tipo', 'activo']


class BillOfMaterialFilter(django_filters.FilterSet):
    class Meta:
        model  = BillOfMaterial
        fields = ['producto_terminado', 'activa', 'version']


class WorkCenterFilter(django_filters.FilterSet):
    class Meta:
        model  = WorkCenter
        fields = ['estado', 'activo']


class ProductionOrderFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date   = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model  = ProductionOrder
        fields = ['estado', 'prioridad', 'centro_trabajo', 'producto']


class InventoryMovementFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(field_name='fecha_movimiento', lookup_expr='date__gte')
    to_date   = django_filters.DateFilter(field_name='fecha_movimiento', lookup_expr='date__lte')

    class Meta:
        model  = InventoryMovement
        fields = ['tipo_movimiento', 'producto', 'orden_produccion']
