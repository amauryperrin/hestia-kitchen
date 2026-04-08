from django.db import models
from apps.auth_foyer.models import User, Foyer
from apps.nutrition.models import Produit

class Lot(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='lots')
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='lots')
    quantite = models.FloatField()
    date_achat = models.DateField()
    date_peremption = models.DateField(null=True, blank=True)
    prix_payer = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lots_crees')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_achat"]

    def __str__(self):
        return f"{self.produit.nom_commercial} - {self.quantite}g"