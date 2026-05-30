# manufacturing/views/bom.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from manufacturing.models           import BillOfMaterial
from manufacturing.serializers.bom  import BillOfMaterialSerializer
from manufacturing.permissions      import IsStaffOrReadOnly
from manufacturing.filters          import BillOfMaterialFilter
from manufacturing.pagination       import StandardPagination


class BillOfMaterialViewSet(viewsets.ModelViewSet):
    queryset           = BillOfMaterial.objects.select_related('producto_terminado').prefetch_related('detalles__materia_prima').all()
    serializer_class   = BillOfMaterialSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = BillOfMaterialFilter
    search_fields      = ['producto_terminado__nombre', 'observaciones']
    ordering_fields    = ['created_at', 'version']
    ordering           = ['-created_at']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = BillOfMaterial.objects.annotate(
            num_detalles=Count('detalles', distinct=True)
        )
        return Response({
            'total':   qs.count(),
            'active':  qs.filter(activa=True).count(),
            'inactive': qs.filter(activa=False).count(),
            'detail': [
                {
                    'id':            b.id,
                    'producto':      b.producto_terminado.nombre,
                    'version':       b.version,
                    'num_detalles':  b.num_detalles,
                    'activa':        b.activa,
                }
                for b in qs.order_by('producto_terminado__nombre')
            ],
        })
