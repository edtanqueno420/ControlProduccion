# manufacturing/views/product.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Sum, Count

from manufacturing.models              import Product
from manufacturing.serializers.product import ProductSerializer
from manufacturing.permissions         import IsStaffOrReadOnly
from manufacturing.filters             import ProductFilter
from manufacturing.pagination          import StandardPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset           = Product.objects.filter(activo=True)
    serializer_class   = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = ProductFilter
    search_fields      = ['nombre', 'codigo_sku', 'descripcion']
    ordering_fields    = ['nombre', 'stock_actual', 'created_at']
    ordering           = ['nombre']

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='restock',
    )
    def restock(self, request, pk=None):
        product = self.get_object()
        try:
            quantity = int(request.data.get('quantity', 0))
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Quantity must be a positive integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.stock_actual += quantity
        product.save(update_fields=['stock_actual'])
        return Response({
            'id':        product.id,
            'nombre':    product.nombre,
            'new_stock': product.stock_actual,
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='available',
    )
    def available(self, request):
        qs   = self.filter_queryset(
            self.get_queryset().filter(stock_actual__gt=0, activo=True)
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ProductSerializer(page, many=True).data
            )
        return Response(ProductSerializer(qs, many=True).data)

    @action(
        detail=False,
        methods=['get'],
        url_path='stats',
    )
    def stats(self, request):
        qs      = Product.objects.all()
        active  = qs.filter(activo=True)
        data    = active.aggregate(
            total_active   = Count('id'),
            total_stock    = Sum('stock_actual'),
        )
        data['total_inactive'] = qs.filter(activo=False).count()
        data['out_of_stock']   = active.filter(stock_actual=0).count()
        data['raw_materials']  = active.filter(tipo='RAW_MATERIAL').count()
        data['finished_goods'] = active.filter(tipo='FINISHED_GOOD').count()
        return Response(data)
