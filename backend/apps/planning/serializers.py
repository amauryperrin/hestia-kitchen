from rest_framework import serializers
from .models import Moment, Repas, LigneRepas
from apps.nutrition.serializers import AlimentSerializer

class MomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moment
        fields = ['id', 'nom', 'ordre', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']
    
class LigneRepasSerializer(serializers.ModelSerializer):
    aliment_detail = AlimentSerializer(source='aliment', read_only=True)
    
    class Meta:
        model = LigneRepas
        fields = [
            'id', 'aliment', 'aliment_detail', 'quantite',
            'calories_snapshot', 'proteines_snapshot', 'glucides_snapshot',
            'lipides_snapshot', 'fibres_snapshot', 'prix_snapshot',
            'lot_peremption_snapshot', 'created_at'
        ]
        read_only_fields = [
            'id', 'calories_snapshot', 'proteines_snapshot', 'glucides_snapshot',
            'lipides_snapshot', 'fibres_snapshot', 'prix_snapshot',
            'lot_peremption_snapshot', 'created_at'
        ]

class RepasSerializer(serializers.ModelSerializer):
    lignes = LigneRepasSerializer(many=True, read_only=True)
    moment_detail = MomentSerializer(source='moment', read_only=True)

    class Meta:
        model = Repas
        fields = ['id', 'date', 'moment', 'moment_detail', 'lignes']
        read_only_fields = ['id']