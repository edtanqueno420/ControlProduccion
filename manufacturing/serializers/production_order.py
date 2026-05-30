# manufacturing/serializers/production_order.py
from rest_framework import serializers
from manufacturing.models import ProductionOrder


class ProductionOrderSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto.nombre', read_only=True
    )
    producto_sku = serializers.CharField(
        source='producto.codigo_sku', read_only=True
    )
    responsable_username = serializers.CharField(
        source='usuario_responsable.username', read_only=True
    )
    centro_trabajo_codigo = serializers.CharField(
        source='centro_trabajo.codigo', read_only=True
    )
    centro_trabajo_nombre = serializers.CharField(
        source='centro_trabajo.nombre_maquina', read_only=True
    )

    class Meta:
        model  = ProductionOrder
        fields = [
            'id', 'codigo_orden', 'producto', 'producto_nombre', 'producto_sku',
            'cantidad_a_producir', 'cantidad_producida',
            'fecha_inicio', 'fecha_fin',
            'estado', 'observaciones', 'prioridad',
            'usuario_responsable', 'responsable_username',
            'centro_trabajo', 'centro_trabajo_codigo', 'centro_trabajo_nombre',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
