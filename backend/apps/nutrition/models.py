from django.db import models
from apps.auth_foyer.models import User, Foyer


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
class Aliment(models.Model):
    nom = models.CharField(max_length=255)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aliments'
    )
    calories = models.FloatField()
    proteines = models.FloatField()
    glucides = models.FloatField()
    lipides = models.FloatField()
    fibres = models.FloatField()
    quantite_reference = models.FloatField(default=100)
    unite_reference = models.CharField(max_length=10, default='g')
    off_id = models.CharField(max_length=100, null=True, blank=True)
    derniere_utilisation = models.DateTimeField(null=True, blank=True)
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='aliments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='aliments_crees')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
class Produit(models.Model):
    nom_commercial = models.CharField(max_length=255)
    aliment = models.ForeignKey(Aliment, on_delete=models.CASCADE, related_name='produits')
    poids_reference = models.FloatField()
    prix = models.FloatField(null=True, blank=True)
    code_barre = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_commercial
    
class Micros(models.Model):
    aliment = models.ForeignKey(Aliment, on_delete=models.CASCADE, related_name='micros')
    nom = models.CharField(max_length=100)
    valeur = models.FloatField()
    unite = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nom} - {self.aliment.nom}"
