# manufacturing/views/inventory_movement.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from manufacturing.models import InventoryMovement, Product
from manufacturing.serializers.inventory_movement import InventoryMovementSerializer
from manufacturing.permissions import IsStaffOrReadOnly
from manufacturing.filters    import InventoryMovementFilter
from manufacturing.pagination import StandardPagination


class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset           = InventoryMovement.objects.select_related(
        'producto', 'usuario', 'orden_produccion'
    ).all()
    serializer_class   = InventoryMovementSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_class    = InventoryMovementFilter
    ordering_fields    = ['fecha_movimiento', 'created_at']
    ordering           = ['-fecha_movimiento']
    http_method_names  = ['get', 'head', 'options']

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='adjust',
    )
    def adjust_stock(self, request):
        producto_id = request.data.get('producto_id')
        nueva_cantidad = request.data.get('nueva_cantidad')
        motivo = request.data.get('motivo', '')

        if not producto_id or nueva_cantidad is None:
            return Response(
                {'error': 'producto_id and nueva_cantidad are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            producto = Product.objects.get(pk=producto_id, activo=True)
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 0:
                raise ValueError
        except (Product.DoesNotExist):
            return Response(
                {'error': 'Product not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'nueva_cantidad must be a non-negative integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock_anterior = producto.stock_actual
        diferencia = nueva_cantidad - stock_anterior
        producto.stock_actual = nueva_cantidad
        producto.save(update_fields=['stock_actual'])

        movement = InventoryMovement.objects.create(
            producto=producto,
            tipo_movimiento='ADJUSTMENT',
            cantidad=diferencia,
            stock_anterior=stock_anterior,
            stock_nuevo=nueva_cantidad,
            motivo=motivo or f'Manual adjustment by {request.user.username}',
            usuario=request.user,
        )

        return Response(
            InventoryMovementSerializer(movement).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='stats',
    )
    def stats(self, request):
        qs = InventoryMovement.objects.all()
        by_type = {
            t: qs.filter(tipo_movimiento=t).count()
            for t, _ in InventoryMovement.MOVEMENT_TYPE_CHOICES
        }
        # Totales por tipo (suma absoluta de cantidades)
        totals = {}
        for t, _ in InventoryMovement.MOVEMENT_TYPE_CHOICES:
            agg = qs.filter(tipo_movimiento=t).aggregate(
                total=Sum('cantidad')
            )['total']
            totals[t] = float(agg or 0)

        return Response({
            'total_movements': qs.count(),
            'by_type':         by_type,
            'totals_by_type':  totals,
        })
