from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Lot
from .serializers import LotSerializer
from apps.auth_foyer.models import MembreFoyer
from apps.nutrition.models import Aliment
from drf_spectacular.utils import extend_schema

def get_foyer(user):
    membre = MembreFoyer.objects.filter(user=user).select_related('foyer').first()
    if membre:
        return membre.foyer
    else:
        return None
    
class LotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=["Lots"],
        responses=LotSerializer(many=True)
    )
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error':'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        lots = Lot.objects.filter(foyer=foyer).select_related('produit__aliment__categorie').order_by('date_achat')
        return Response(LotSerializer(lots, many=True).data)
    
    
    @extend_schema(
        tags=["Lots"],
        request=LotSerializer,
        responses=LotSerializer
    )
    def post(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error':'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(foyer=foyer, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LotDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_lot(self, pk, foyer):
        try:
            return Lot.objects.get(pk=pk, foyer=foyer)
        except Lot.DoesNotExist:
            return None
    
    @extend_schema(
        tags=["Lots"],
        responses=LotSerializer
    )
    def get(self, request, pk):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        lot = self.get_lot(pk, foyer)
        if not lot:
            return Response({'error':'Lot introuvable'}, status=status.HTTP_404_NOT_FOUND)
        return Response(LotSerializer(lot).data)
    
    @extend_schema(
        tags=["Lots"],
        request=LotSerializer,
        responses=LotSerializer
    )
    def put(self, request, pk):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        lot = self.get_lot(pk, foyer)
        if not lot:
            return Response({'error':'Lot introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LotSerializer(lot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=["Lots"],
        responses={204: None}
    )
    def delete(self, request, pk):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        
        lot = self.get_lot(pk, foyer)
        if not lot:
            return Response({'error':'Lot introuvable'}, status=status.HTTP_404_NOT_FOUND)
        lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StockAlimentView(APIView):
    """Stock total par aliment — somme des lots actifs"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=["Inventory"],
        responses=None
    )
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        
        lots = Lot.objects.filter(foyer=foyer, quantite__gt=0).select_related('produit__aliment__categorie')
        stock = {}
        for lot in lots:
            aliment = lot.aliment
            if aliment.id not in stock:
                stock[aliment.id] = {
                    'aliment_id': aliment.id,
                    'nom': aliment.nom,
                    'categorie': aliment.categorie.nom if aliment.categorie else None,
                    'quantite_totale': 0,
                    'lots': []
                }
            stock[aliment.id]['quantite_totale'] += lot.quantite
            stock[aliment.id]['lots'].append(LotSerializer(lot).data)
        return Response(list(stock.values()))