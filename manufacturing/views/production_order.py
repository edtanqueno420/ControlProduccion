# manufacturing/views/production_order.py
from django.utils import timezone
from django.db.models import Count, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from manufacturing.models import ProductionOrder, Product, BillOfMaterial, InventoryMovement
from manufacturing.serializers.production_order import ProductionOrderSerializer
from manufacturing.permissions import IsOwnerOrStaff
from manufacturing.filters    import ProductionOrderFilter
from manufacturing.pagination import StandardPagination


class ProductionOrderViewSet(viewsets.ModelViewSet):
    serializer_class   = ProductionOrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_class    = ProductionOrderFilter
    ordering_fields    = ['created_at', 'cantidad_a_producir', 'prioridad']
    ordering           = ['-created_at']
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        if self.request.user.is_staff:
            return (
                ProductionOrder.objects
                .select_related('producto', 'usuario_responsable', 'centro_trabajo')
                .all()
            )
        return (
            ProductionOrder.objects
            .filter(usuario_responsable=self.request.user)
            .select_related('producto', 'centro_trabajo')
        )

    def perform_create(self, serializer):
        serializer.save(usuario_responsable=self.request.user)

    def _validar_stock_materia_prima(self, producto, cantidad_a_producir):
        """Valida que exista suficiente materia prima para la BOM activa."""
        try:
            bom = BillOfMaterial.objects.get(
                producto_terminado=producto, activa=True
            )
        except BillOfMaterial.DoesNotExist:
            return None, 'No active BOM found for this product.'

        faltantes = []
        for detalle in bom.detalles.select_related('materia_prima'):
            cantidad_necesaria = (
                float(detalle.cantidad_requerida) * cantidad_a_producir
                * (1 + float(detalle.desperdicio_porcentaje) / 100)
            )
            if detalle.materia_prima.stock_actual < cantidad_necesaria:
                faltantes.append({
                    'material':   detalle.materia_prima.nombre,
                    'necesario':  cantidad_necesaria,
                    'disponible': detalle.materia_prima.stock_actual,
                })

        if faltantes:
            return faltantes, 'Insufficient raw material stock.'
        return None, None

    def _consumir_materia_prima(self, orden):
        """Genera movimientos de inventario negativos por consumo de materia prima."""
        bom = BillOfMaterial.objects.get(
            producto_terminado=orden.producto, activa=True
        )
        movs = []
        for detalle in bom.detalles.select_related('materia_prima'):
            cantidad = (
                float(detalle.cantidad_requerida) * orden.cantidad_producida
                * (1 + float(detalle.desperdicio_porcentaje) / 100)
            )
            producto = detalle.materia_prima
            stock_anterior = producto.stock_actual
            producto.stock_actual = max(
                0, producto.stock_actual - int(cantidad)
            )
            producto.save(update_fields=['stock_actual'])

            movs.append(InventoryMovement.objects.create(
                producto=producto,
                tipo_movimiento='PRODUCTION_CONSUMPTION',
                cantidad=-cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=producto.stock_actual,
                motivo=f'Consumption for order {orden.codigo_orden}',
                orden_produccion=orden,
                usuario=orden.usuario_responsable,
            ))
        return movs

    def _ingresar_producto_terminado(self, orden):
        """Genera movimiento de inventario positivo por producto terminado."""
        producto = orden.producto
        stock_anterior = producto.stock_actual
        producto.stock_actual += orden.cantidad_producida
        producto.save(update_fields=['stock_actual'])

        InventoryMovement.objects.create(
            producto=producto,
            tipo_movimiento='PRODUCTION_INPUT',
            cantidad=orden.cantidad_producida,
            stock_anterior=stock_anterior,
            stock_nuevo=producto.stock_actual,
            motivo=f'Production input from order {orden.codigo_orden}',
            orden_produccion=orden,
            usuario=orden.usuario_responsable,
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='start',
    )
    def start_production(self, request, pk=None):
        order = self.get_object()
        if order.estado != 'DRAFT':
            return Response(
                {'error': f'Cannot start an order with status "{order.estado}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar stock de materia prima
        faltantes, error = self._validar_stock_materia_prima(
            order.producto, order.cantidad_a_producir
        )
        if error:
            return Response(
                {'error': error, 'details': faltantes},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar exclusividad del centro de trabajo
        if ProductionOrder.objects.filter(
            centro_trabajo=order.centro_trabajo,
            estado='IN_PROGRESS',
        ).exclude(pk=order.pk).exists():
            return Response(
                {'error': 'Work center already has an order in progress.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.estado = 'IN_PROGRESS'
        order.fecha_inicio = timezone.now()
        order.save(update_fields=['estado', 'fecha_inicio'])
        return Response(ProductionOrderSerializer(order).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='complete',
    )
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.estado != 'IN_PROGRESS':
            return Response(
                {'error': f'Only in-progress orders can be completed. Current: {order.estado}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cantidad = request.data.get('cantidad_producida')
        if cantidad is not None:
            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response(
                    {'error': 'cantidad_producida must be a positive integer.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.cantidad_producida = cantidad
        else:
            order.cantidad_producida = order.cantidad_a_producir

        order.estado = 'FINISHED'
        order.fecha_fin = timezone.now()
        order.save(update_fields=[
            'estado', 'cantidad_producida', 'fecha_fin'
        ])

        # Consumo automático de materia prima
        self._consumir_materia_prima(order)
        # Ingreso automático de producto terminado
        self._ingresar_producto_terminado(order)

        return Response(ProductionOrderSerializer(order).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='pause',
    )
    def pause(self, request, pk=None):
        order = self.get_object()
        if order.estado != 'IN_PROGRESS':
            return Response(
                {'error': f'Only in-progress orders can be paused. Current: {order.estado}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.estado = 'PAUSED'
        order.save(update_fields=['estado'])
        return Response(ProductionOrderSerializer(order).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='cancel',
    )
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.estado in ['FINISHED', 'CANCELLED']:
            return Response(
                {'error': f'Cannot cancel an order with status "{order.estado}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.estado = 'CANCELLED'
        order.fecha_fin = timezone.now()
        order.save(update_fields=['estado', 'fecha_fin'])
        return Response(ProductionOrderSerializer(order).data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAdminUser],
        url_path='stats',
    )
    def stats(self, request):
        qs = ProductionOrder.objects.all()
        by_status = {
            s: qs.filter(estado=s).count()
            for s, _ in ProductionOrder.STATUS_CHOICES
        }
        by_priority = {
            p: qs.filter(prioridad=p).count()
            for p, _ in ProductionOrder.PRIORITY_CHOICES
        }
        return Response({
            'total_orders':  qs.count(),
            'by_status':     by_status,
            'by_priority':   by_priority,
        })
