# manufacturing/serializers/product.py
from rest_framework import serializers
from manufacturing.models import Product


class ProductSerializer(serializers.ModelSerializer):
    stock_suficiente = serializers.SerializerMethodField()
    es_materia_prima = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'codigo_sku', 'nombre', 'descripcion',
            'tipo', 'stock_actual', 'unidad_medida', 'stock_minimo',
            'stock_suficiente', 'es_materia_prima',
            'activo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_stock_suficiente(self, obj):
        return obj.stock_suficiente

    def get_es_materia_prima(self, obj):
        return obj.es_materia_prima

    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value
