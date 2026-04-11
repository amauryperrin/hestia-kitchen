from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Categorie, Aliment, Produit
from .serializers import CategorieSerializer, AlimentSerializer, ProduitSerializer
from apps.auth_foyer.models import MembreFoyer

def get_foyer(user):
    membre = MembreFoyer.objects.filter(user=user).select_related('foyer').first()
    if membre:
        return membre.foyer 
    else:
        return None
    

class CategorieListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Categorie.objects.all()
        return Response(CategorieSerializer(categories, many=True).data)
    
    def post(self, request):
        serializer = CategorieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AlimentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        aliments = Aliment.objects.filter(foyer=foyer).select_related('categorie').order_by('-derniere_utilisation')
        return Response(AlimentSerializer(aliments, many=True).data)

    def post(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlimentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(foyer=foyer, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AlimentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_aliment(self, pk, foyer):
        try:
            return Aliment.objects.get(pk=pk, foyer=foyer)
        except Aliment.DoesNotExist:
            return None
    
    def get(self, request, pk):
        foyer = get_foyer(request.user)
        aliment =  self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error', 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AlimentSerializer(aliment).data)
    
    def put(self, request, pk):
        foyer = get_foyer(request.user)
        aliment = self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error', 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlimentSerializer(aliment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        foyer = get_foyer(request.user)
        aliment = self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error', 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        aliment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            
            