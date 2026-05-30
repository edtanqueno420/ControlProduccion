# manufacturing/models/product.py
from django.db import models


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('RAW_MATERIAL',      'Raw Material'),
        ('IN_PROCESS',        'In Process'),
        ('FINISHED_GOOD',     'Finished Good'),
    ]

    codigo_sku    = models.CharField(max_length=50, unique=True)
    nombre        = models.CharField(max_length=200)
    descripcion   = models.TextField(blank=True, default='')
    tipo          = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
    )
    stock_actual  = models.PositiveIntegerField(default=0)
    unidad_medida = models.CharField(max_length=20, default='units')
    stock_minimo  = models.PositiveIntegerField(default=0)
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo_sku} — {self.nombre}'

    @property
    def stock_suficiente(self):
        return self.stock_actual >= self.stock_minimo

    @property
    def es_materia_prima(self):
        return self.tipo == 'RAW_MATERIAL'
