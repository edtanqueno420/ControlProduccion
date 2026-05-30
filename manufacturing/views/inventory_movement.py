from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Sum

from manufacturing.models import InventoryMovement, Product
from manufacturing.serializers.inventory_movement import InventoryMovementSerializer


class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all().order_by('-created_at')
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='adjust')
    def adjust(self, request):
        """
        Endpoint personalizado para ajustar de manera manual el stock de un producto.
        Mapea a la perfección con los tests de ajuste de inventario.
        """
        producto_id = request.data.get('producto_id')
        nueva_cantidad = request.data.get('nueva_cantidad')
        motivo = request.data.get('motivo', 'Adjustment')

        # Validación de campos requeridos (test_adjust_missing_fields)
        if producto_id is None or nueva_cantidad is None:
            return Response(
                {"error": "producto_id y nueva_cantidad son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validación de existencia del producto (test_adjust_invalid_product)
        producto = get_object_or_404(Product, id=producto_id)

        # Lógica transaccional para actualizar el producto y crear el movimiento
        with transaction.atomic():
            stock_anterior = producto.stock_actual
            stock_nuevo = float(nueva_cantidad)
            diferencia_cantidad = stock_nuevo - float(stock_anterior)

            # Actualizar el stock del producto real (test_adjust_stock_updates_product)
            producto.stock_actual = stock_nuevo
            producto.save()

            # Guardar el registro histórico en InventoryMovement
            movimiento = InventoryMovement.objects.create(
                producto=producto,
                tipo_movimiento='ADJUSTMENT',
                cantidad=abs(diferencia_cantidad),
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                motivo=motivo,
                usuario=request.user
            )

        serializer = self.get_serializer(movimiento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Endpoint para retornar las estadísticas del inventario (test_stats_returns_expected_fields).
        """
        total_movements = self.queryset.count()
        
        # Agrupaciones básicas de base de datos
        by_type = self.queryset.values('tipo_movimiento').annotate(count=Count('id'))
        totals_by_type = self.queryset.values('tipo_movimiento').annotate(total=Sum('cantidad'))

        data = {
            'total_movements': total_movements,
            'by_type': {item['tipo_movimiento']: item['count'] for item in by_type},
            'totals_by_type': {item['tipo_movimiento']: item['total'] or 0 for item in totals_by_type}
        }
        return Response(data, status=status.HTTP_200_OK)