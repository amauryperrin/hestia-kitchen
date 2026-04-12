from rest_framework import serializers
from .models import User, Foyer, MembreFoyer
from apps.planning.models import Moment

import random
import string


def generate_foyer_code():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = 'FH-' + ''.join(random.choices(chars, k=6))
        if not Foyer.objects.filter(code=code).exists():
            return code

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified', 'calories_cibles', 
                  'proteines_cibles', 'glucides_cibles', 'lipides_cibles', 'fibres_cibles', 'created_at']
        read_only_fields = ['ids', 'is_verified', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        code = generate_foyer_code()
        foyer = Foyer.objects.create(nom=f"Foyer de {user.first_name}", code=code)
        MembreFoyer.objects.create(user=user, foyer=foyer, role='admin')
        
        moments_defaut = [
            {'nom': 'Petit-déjeuner', 'ordre': 1, 'is_default': True},
            {'nom': 'Déjeuner', 'ordre': 2, 'is_default': True},
            {'nom': 'Collation', 'ordre': 3, 'is_default': True},
            {'nom': 'Dîner', 'ordre': 4, 'is_default': True},
        ]
        
        for moment in moments_defaut:
            Moment.objects.create(foyer=foyer, **moment)
        
        return user

class FoyerSerializer(serializers.ModelSerializer):
    membres_count = serializers.SerializerMethodField()

    class Meta:
        model = Foyer
        fields = ['id', 'nom', 'code', 'membres_count', 'created_at']

    def get_membres_count(self, obj):
        return obj.membres.count()

class MembreFoyerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)

    class Meta:
        model = MembreFoyer
        fields = ['id', 'user', 'role', 'joined_at']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)