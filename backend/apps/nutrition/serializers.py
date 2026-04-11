from rest_framework import serializers
from .models import Categorie, Aliment, Produit

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']
        

class AlimentSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Aliment
        fields = [
            'id', 'nom', 'categorie', 'categorie_id',
            'calories', 'proteines', 'glucides', 'lipides', 'fibres',
            'quantite_reference', 'unite_reference',
            'off_id', 'derniere_utilisation', 'created_at'
        ]
        read_only_fields = ['id', 'derniere_utilisation', 'created_at']

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom_commercial', 'aliment', 'poids_reference', 'prix', 'code_barre', 'created_at']
        read_only_fields = ['id', 'created_at']