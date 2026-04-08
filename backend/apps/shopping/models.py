from django.db import models

from apps.auth_foyer.models import User, Foyer
from apps.nutrition.models import Aliment, Produit
from apps.inventory.models import Lot

class ListeCourses(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('courses_en_cours', 'Courses en cours'),
    ]

    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name=('listes_courses'))
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.foyer.nom} - {self.statut}"
    
class LigneCourses(models.Model):
    liste = models.ForeignKey(ListeCourses, on_delete=models.CASCADE, related_name='lignes')
    aliment = models.ForeignKey(Aliment, on_delete=models.SET_NULL, null=True, blank=True, related_name='lignes_courses')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True, related_name='lignes_courses')
    nom_libre = models.CharField(max_length=255, null=True, blank=True)
    quantite = models.FloatField(null=True, blank=True)
    is_checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lignes_courses')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lignes_courses_creees')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.aliment.nom if self.aliment else self.nom_libre