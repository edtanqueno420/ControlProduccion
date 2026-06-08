# manufacturing/views/bom.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from manufacturing.models           import BillOfMaterial, BillOfMaterialDetail
from manufacturing.serializers.bom  import BillOfMaterialSerializer, BillOfMaterialDetailSerializer, BillOfMaterialDetailWriteSerializer
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


class BillOfMaterialDetailViewSet(viewsets.ModelViewSet):
    queryset           = BillOfMaterialDetail.objects.select_related('materia_prima').all()
    permission_classes = [IsStaffOrReadOnly]
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['lista_materiales']
    ordering_fields    = ['created_at']
    ordering           = ['created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BillOfMaterialDetailWriteSerializer
        return BillOfMaterialDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        read = BillOfMaterialDetailSerializer(serializer.instance)
        return Response(read.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read = BillOfMaterialDetailSerializer(serializer.instance)
        return Response(read.data)
