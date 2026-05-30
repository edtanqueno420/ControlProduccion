# manufacturing/views/work_center.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from manufacturing.models              import WorkCenter
from manufacturing.serializers.work_center import WorkCenterSerializer
from manufacturing.permissions         import IsStaffOrReadOnly
from manufacturing.filters             import WorkCenterFilter
from manufacturing.pagination          import StandardPagination


class WorkCenterViewSet(viewsets.ModelViewSet):
    queryset           = WorkCenter.objects.all()
    serializer_class   = WorkCenterSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = WorkCenterFilter
    search_fields      = ['codigo', 'nombre_maquina', 'descripcion']
    ordering_fields    = ['codigo', 'capacidad_diaria']
    ordering           = ['codigo']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = WorkCenter.objects.annotate(
            num_orders=Count('production_orders', distinct=True)
        )
        return Response({
            'total':       qs.count(),
            'active':      qs.filter(estado='ACTIVE').count(),
            'maintenance': qs.filter(estado='MAINTENANCE').count(),
            'inactive':    qs.filter(estado='INACTIVE').count(),
            'detail': [
                {
                    'id':           w.id,
                    'codigo':       w.codigo,
                    'maquina':      w.nombre_maquina,
                    'estado':       w.estado,
                    'num_orders':   w.num_orders,
                }
                for w in qs.order_by('codigo')
            ],
        })
