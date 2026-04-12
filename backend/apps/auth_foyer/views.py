import random
import string
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer, FoyerSerializer, MembreFoyerSerializer, LoginSerializer
from .models import User, Foyer, MembreFoyer
from drf_spectacular.utils import extend_schema

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses=UserSerializer
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses=UserSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                })
            return Response({'error': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RegisterSerializer,
        responses=UserSerializer
    )
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class FoyerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoyerSerializer,
        responses=UserSerializer
    )
    
    def get(self, request):
        membre = MembreFoyer.objects.filter(user=request.user).select_related('foyer').first()
        if not membre:
            return Response({'error': 'Vous n\'êtes dans aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FoyerSerializer(membre.foyer).data)

class RejoindreFoyerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoyerSerializer,
        responses=UserSerializer
    )
    
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code foyer Requis'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            foyer = Foyer.objects.get(code=code)
        except Foyer.DoesNotExist:
            return Response({'error': 'Foyer Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        if MembreFoyer.objects.filter(user=request.user, foyer=foyer).exists():
            return Response({'error': 'Vous êtes déjà membre de ce foyer'}, status=status.HTTP_400_BAD_REQUEST)
        MembreFoyer.objects.filter(user=request.user).delete()
        MembreFoyer.objects.create(user=request.user, foyer=foyer, role='membre')
        return Response(FoyerSerializer(foyer).data)

class MembresFoyerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=MembreFoyerSerializer,
        responses=UserSerializer
    )
    
    def get(self, request):
        membre = MembreFoyer.objects.filter(user=request.user).select_related('foyer').first()
        if not membre:
            return Response({'error':'VOus n\'êtes membre d\'aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        membres = MembreFoyer.objects.filter(foyer=membre.foyer).select_related('user')
        return Response(MembreFoyerSerializer(membres, many=True).data)