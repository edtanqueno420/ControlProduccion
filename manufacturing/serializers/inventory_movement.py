# manufacturing/serializers/inventory_movement.py
from rest_framework import serializers
from manufacturing.models import InventoryMovement


class InventoryMovementSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto.nombre', read_only=True
    )
    producto_sku = serializers.CharField(
        source='producto.codigo_sku', read_only=True
    )
    usuario_username = serializers.CharField(
        source='usuario.username', read_only=True
    )
    orden_codigo = serializers.CharField(
        source='orden_produccion.codigo_orden', read_only=True,
    )

    class Meta:
        model  = InventoryMovement
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_sku',
            'tipo_movimiento', 'cantidad',
            'stock_anterior', 'stock_nuevo',
            'motivo', 'orden_produccion', 'orden_codigo',
            'usuario', 'usuario_username',
            'fecha_movimiento', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'fecha_movimiento', 'created_at', 'updated_at']
