# manufacturing/models/profile.py
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN',      'Admin'),
        ('SUPERVISOR', 'Supervisor'),
        ('OPERARIO',   'Operario'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='OPERARIO',
    )

    class Meta:
        verbose_name        = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'{self.user.username} — {self.role}'
