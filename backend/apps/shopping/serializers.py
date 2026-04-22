from rest_framework import serializers
from .models import ListeCourses, LigneCourses
from apps.nutrition.serializers import AlimentSerializer, ProduitSerializer

class LigneCourseSerializer(serializers.ModelSerializer):
    aliment_detail = AlimentSerializer(source='aliment', read_only=True)
    produit_detail = ProduitSerializer(source='produit', read_only=True)

    class Meta:
        model = LigneCourses
        fields = [
            'id', 'liste', 'aliment', 'aliment_detail',
            'produit', 'produit_detail', 'nom_libre',
            'quantite', 'is_checked', 'checked_at',
            'lot', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'liste', 'checked_at', 'created_by', 'created_at']

class ListeCoursesSerializer(serializers.ModelSerializer):
    lignes= LigneCourseSerializer(many=True, read_only=True)

    class Meta:
        model = ListeCourses
        fields = ['id', 'foyer', 'statut', 'lignes', 'created_at']
        read_only_fields = ['id', 'foyer', 'created_at']