# manufacturing/admin.py
from django.contrib import admin
from manufacturing.models import (
    Profile, Product,
    BillOfMaterial, BillOfMaterialDetail,
    WorkCenter, ProductionOrder, InventoryMovement,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'role']
    list_filter   = ['role']
    search_fields = ['user__username']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'codigo_sku', 'nombre', 'tipo', 'stock_actual', 'unidad_medida', 'activo']
    list_filter   = ['tipo', 'activo']
    search_fields = ['nombre', 'codigo_sku', 'descripcion']
    list_editable = ['stock_actual', 'activo']


class BillOfMaterialDetailInline(admin.TabularInline):
    model  = BillOfMaterialDetail
    extra  = 1
    fields = ['materia_prima', 'cantidad_requerida', 'desperdicio_porcentaje']


@admin.register(BillOfMaterial)
class BillOfMaterialAdmin(admin.ModelAdmin):
    list_display    = ['id', 'producto_terminado', 'version', 'cantidad_base', 'activa', 'created_at']
    list_filter     = ['activa']
    search_fields   = ['producto_terminado__nombre']
    inlines         = [BillOfMaterialDetailInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BillOfMaterialDetail)
class BillOfMaterialDetailAdmin(admin.ModelAdmin):
    list_display  = ['id', 'lista_materiales', 'materia_prima', 'cantidad_requerida', 'desperdicio_porcentaje']
    list_filter   = ['lista_materiales']


@admin.register(WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display  = ['id', 'codigo', 'nombre_maquina', 'estado', 'capacidad_diaria', 'activo']
    list_filter   = ['estado', 'activo']
    search_fields = ['codigo', 'nombre_maquina', 'descripcion']
    list_editable = ['estado', 'activo']


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display    = ['id', 'codigo_orden', 'producto', 'cantidad_a_producir', 'estado', 'prioridad', 'usuario_responsable', 'centro_trabajo', 'created_at']
    list_filter     = ['estado', 'prioridad']
    search_fields   = ['codigo_orden', 'producto__nombre', 'observaciones']
    readonly_fields = ['created_at', 'updated_at']
    list_editable   = ['estado']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display  = ['id', 'producto', 'tipo_movimiento', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha_movimiento']
    list_filter   = ['tipo_movimiento']
    search_fields = ['producto__nombre', 'motivo']
    readonly_fields = ['fecha_movimiento', 'created_at', 'updated_at']
