from django.db import models
from apps.auth_foyer.models import User, Foyer
from apps.nutrition.models import Aliment

class Moment(models.Model):
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='moments')
    nom = models.CharField(max_length=100)
    ordre = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.foyer.nom} - {self.nom}"
    
class Repas(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'repas')
    date = models.DateField()
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='repas')

    class Meta:
        unique_together = ('user', 'date', 'moment')

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.moment.nom}"
    
class LigneRepas(models.Model):
    planning = models.ForeignKey(Repas, on_delete=models.CASCADE, related_name='lignes')
    aliment = models.ForeignKey(Aliment, on_delete=models.PROTECT, related_name='lignes_repas')
    quantite = models.FloatField()
    photo = models.CharField(max_length=500, null=True, blank=True)
    calories_snapshot = models.FloatField()
    proteines_snapshot = models.FloatField()
    glucides_snapshot = models.FloatField()
    lipides_snapshot = models.FloatField()
    fibres_snapshot = models.FloatField()
    prix_snapshot = models.FloatField(null=True, blank=True)
    lot_peremption_snapshot = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.aliment.nom} - {self.quantite}g"

