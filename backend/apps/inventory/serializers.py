from rest_framework import serializers
from .models import Lot, Produit
from apps.nutrition.serializers import ProduitSerializer

class LotSerializer(serializers.ModelSerializer):
    produit_detail = ProduitSerializer(source='produit', read_only=True)
    produit = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Lot
        fields = [
            'id', 'aliment', 'produit', 'produit_detail', 'foyer',
            'quantite', 'date_achat', 'date_peremption',
            'prix_payer', 'created_by', 'created_at'
            ]
        read_only_fields = ['id', 'foyer', 'created_by', 'created_at']