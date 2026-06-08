# manufacturing/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from manufacturing.views.health    import health_check
from manufacturing.views.auth      import RegisterView, LogoutView
from manufacturing.views.user      import UserViewSet
from manufacturing.views.product   import ProductViewSet
from manufacturing.views.bom       import BillOfMaterialViewSet, BillOfMaterialDetailViewSet
from manufacturing.views.work_center import WorkCenterViewSet
from manufacturing.views.production_order import ProductionOrderViewSet
from manufacturing.views.inventory_movement import InventoryMovementViewSet
from manufacturing.serializers.auth import CustomTokenView

router = DefaultRouter()
router.register('users',               UserViewSet,               basename='user')
router.register('products',             ProductViewSet,            basename='product')
router.register('bill-of-materials',    BillOfMaterialViewSet,     basename='bill-of-material')
router.register('bom-details',          BillOfMaterialDetailViewSet, basename='bom-detail')
router.register('work-centers',         WorkCenterViewSet,         basename='work-center')
router.register('production-orders',    ProductionOrderViewSet,    basename='production-order')
router.register('inventory-movements',  InventoryMovementViewSet,  basename='inventory-movement')

urlpatterns = [
    path('health/',             health_check),
    path('auth/register/',      RegisterView.as_view()),
    path('auth/login/',         CustomTokenView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/token/verify/',  TokenVerifyView.as_view()),
    path('auth/logout/',        LogoutView.as_view()),
    path('', include(router.urls)),
]
