# manufacturing/models/production_order.py
from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .work_center import WorkCenter


class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT',       'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED',      'Paused'),
        ('FINISHED',    'Finished'),
        ('CANCELLED',   'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('LOW',   'Low'),
        ('MEDIUM','Medium'),
        ('HIGH',  'High'),
    ]

    codigo_orden        = models.CharField(max_length=50, unique=True)
    producto            = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='production_orders',
    )
    cantidad_a_producir = models.PositiveIntegerField()
    cantidad_producida  = models.PositiveIntegerField(default=0)
    fecha_inicio        = models.DateTimeField(null=True, blank=True)
    fecha_fin           = models.DateTimeField(null=True, blank=True)
    estado              = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
    )
    observaciones       = models.TextField(blank=True, default='')
    prioridad           = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
    )
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='production_orders',
    )
    centro_trabajo      = models.ForeignKey(
        WorkCenter,
        on_delete=models.PROTECT,
        related_name='production_orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Production Order'
        verbose_name_plural = 'Production Orders'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.codigo_orden} — {self.producto.nombre} ({self.estado})'
