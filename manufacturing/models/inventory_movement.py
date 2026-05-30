# manufacturing/models/inventory_movement.py
from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .production_order import ProductionOrder


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('INCOMING',              'Incoming'),
        ('OUTGOING',              'Outgoing'),
        ('ADJUSTMENT',            'Adjustment'),
        ('PRODUCTION_CONSUMPTION','Production Consumption'),
        ('PRODUCTION_INPUT',      'Production Input'),
    ]

    producto           = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='inventory_movements',
    )
    tipo_movimiento    = models.CharField(
        max_length=25,
        choices=MOVEMENT_TYPE_CHOICES,
    )
    cantidad           = models.DecimalField(max_digits=12, decimal_places=2)
    stock_anterior     = models.DecimalField(max_digits=12, decimal_places=2)
    stock_nuevo        = models.DecimalField(max_digits=12, decimal_places=2)
    motivo             = models.TextField(blank=True, default='')
    orden_produccion   = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements',
    )
    usuario            = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='inventory_movements',
    )
    fecha_movimiento   = models.DateTimeField(auto_now_add=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Inventory Movement'
        verbose_name_plural = 'Inventory Movements'
        ordering            = ['-fecha_movimiento']

    def __str__(self):
        return f'{self.tipo_movimiento} — {self.producto.nombre} x{self.cantidad}'
