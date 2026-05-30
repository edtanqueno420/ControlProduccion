# manufacturing/models/work_center.py
from django.db import models


class WorkCenter(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE',        'Active'),
        ('MAINTENANCE',   'Maintenance'),
        ('INACTIVE',      'Inactive'),
    ]

    codigo         = models.CharField(max_length=50, unique=True)
    nombre_maquina = models.CharField(max_length=200)
    descripcion    = models.TextField(blank=True, default='')
    estado         = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
    )
    capacidad_diaria = models.PositiveIntegerField(default=1)
    activo         = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} — {self.nombre_maquina}'
