# manufacturing/serializers/work_center.py
from rest_framework import serializers
from manufacturing.models import WorkCenter


class WorkCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model  = WorkCenter
        fields = [
            'id', 'codigo', 'nombre_maquina', 'descripcion',
            'estado', 'capacidad_diaria', 'activo',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
