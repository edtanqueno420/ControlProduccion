# manufacturing/models/bom.py
from django.db import models
from .product import Product


class BillOfMaterial(models.Model):
    producto_terminado = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='boms',
        limit_choices_to={'tipo': 'FINISHED_GOOD'},
    )
    version       = models.PositiveIntegerField(default=1)
    cantidad_base = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    activa        = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, default='')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Bill of Material'
        verbose_name_plural = 'Bill of Materials'
        ordering            = ['-created_at']
        unique_together     = ['producto_terminado', 'version']

    def __str__(self):
        return f'BOM #{self.id} — {self.producto_terminado.nombre} v{self.version}'


class BillOfMaterialDetail(models.Model):
    lista_materiales    = models.ForeignKey(
        BillOfMaterial,
        on_delete=models.CASCADE,
        related_name='detalles',
    )
    materia_prima       = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='bom_details',
        limit_choices_to={'tipo': 'RAW_MATERIAL'},
    )
    cantidad_requerida  = models.DecimalField(max_digits=10, decimal_places=2)
    desperdicio_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'BOM Detail'
        verbose_name_plural = 'BOM Details'

    def __str__(self):
        return f'{self.materia_prima.nombre} x{self.cantidad_requerida}'

    @property
    def cantidad_con_desperdicio(self):
        return float(self.cantidad_requerida) * (1 + float(self.desperdicio_porcentaje) / 100)
