# manufacturing/models/__init__.py
from .profile import Profile
from .product import Product
from .bom import BillOfMaterial, BillOfMaterialDetail
from .work_center import WorkCenter
from .production_order import ProductionOrder
from .inventory_movement import InventoryMovement

__all__ = [
    'Profile', 'Product',
    'BillOfMaterial', 'BillOfMaterialDetail',
    'WorkCenter', 'ProductionOrder', 'InventoryMovement',
]
