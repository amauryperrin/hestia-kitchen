from django.db import models

from apps.auth_foyer.models import User, Foyer
from apps.inventory.models import Lot

class Notification(models.Model):
    TYPE_CHOICES = [
        ('peremption_j1', 'Péremption J-1'),
        ('peremption_j0', 'Péremption J-0'),
    ]

    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.type}"