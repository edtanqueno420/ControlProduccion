# manufacturing/serializers/bom.py
from rest_framework import serializers
from manufacturing.models import BillOfMaterial, BillOfMaterialDetail, Product


class BillOfMaterialDetailSerializer(serializers.ModelSerializer):
    materia_prima_nombre = serializers.CharField(
        source='materia_prima.nombre', read_only=True
    )
    materia_prima_sku = serializers.CharField(
        source='materia_prima.codigo_sku', read_only=True
    )
    cantidad_con_desperdicio = serializers.SerializerMethodField()

    class Meta:
        model  = BillOfMaterialDetail
        fields = [
            'id', 'materia_prima', 'materia_prima_nombre', 'materia_prima_sku',
            'cantidad_requerida', 'desperdicio_porcentaje',
            'cantidad_con_desperdicio', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_cantidad_con_desperdicio(self, obj):
        return obj.cantidad_con_desperdicio


class BillOfMaterialSerializer(serializers.ModelSerializer):
    detalles = BillOfMaterialDetailSerializer(many=True, read_only=True)
    producto_terminado_nombre = serializers.CharField(
        source='producto_terminado.nombre', read_only=True
    )
    producto_terminado_sku = serializers.CharField(
        source='producto_terminado.codigo_sku', read_only=True
    )
    num_detalles = serializers.SerializerMethodField()

    class Meta:
        model  = BillOfMaterial
        fields = [
            'id', 'producto_terminado', 'producto_terminado_nombre',
            'producto_terminado_sku', 'version', 'cantidad_base',
            'activa', 'observaciones', 'num_detalles',
            'detalles', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_num_detalles(self, obj):
        return obj.detalles.count()
