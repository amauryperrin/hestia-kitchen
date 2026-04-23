from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Categorie, Aliment, Produit
from .serializers import CategorieSerializer, AlimentSerializer, ProduitSerializer
from apps.auth_foyer.models import MembreFoyer
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
import redis
from django.conf import settings
from django.core.cache import cache

r = redis.from_url(settings.REDIS_URL)

def check_off_rate_limit():
    key = 'off_requests_count'
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    return count <= 8

def get_foyer(user):
    membre = MembreFoyer.objects.filter(user=user).select_related('foyer').first()
    if membre:
        return membre.foyer 
    else:
        return None
    

class CategorieListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=["Nutrition"],
        responses=CategorieSerializer
    )
    def get(self, request):
        categories = Categorie.objects.all()
        return Response(CategorieSerializer(categories, many=True).data)
    
    @extend_schema(
        tags=["Nutrition"],
        request=CategorieSerializer,
        responses=CategorieSerializer
    )
    def post(self, request):
        serializer = CategorieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AlimentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Nutrition"],
        responses=AlimentSerializer
    )
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        aliments = Aliment.objects.filter(foyer=foyer).select_related('categorie').order_by('-derniere_utilisation')
        return Response(AlimentSerializer(aliments, many=True).data)

    
    @extend_schema(
        tags=["Nutrition"],
        request=AlimentSerializer,
        responses=AlimentSerializer
    )
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
    
    
    @extend_schema(
        tags=["Nutrition"],
        responses=AlimentSerializer
    )
    def get(self, request, pk):
        foyer = get_foyer(request.user)
        aliment =  self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error': 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AlimentSerializer(aliment).data)
    
    @extend_schema(
        tags=["Nutrition"],
        request=AlimentSerializer,
        responses=AlimentSerializer
    )
    def put(self, request, pk):
        foyer = get_foyer(request.user)
        aliment = self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error': 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlimentSerializer(aliment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=["Nutrition"],
        responses={204: None}
    )
    def delete(self, request, pk):
        foyer = get_foyer(request.user)
        aliment = self.get_aliment(pk, foyer)
        if not aliment:
            return Response({'error': 'Aliment Introuvable'}, status=status.HTTP_404_NOT_FOUND)
        aliment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            
class OpenFoodFactsSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Nutrition"], parameters=[
        OpenApiParameter(name='q', description='Terme de recherche', required=True, type=str)
    ], responses=None)
    def get(self, request):
        q = request.query_params.get('q')
        if not q:
            return Response({'error': 'Paramètre q requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cache Redis
        cache_key = f'off_search_{q.lower().strip()}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Rate Limit
        if not check_off_rate_limit():
            return Response({'error': 'Trop de requêtes vers OpenFoodFacts, réessayez dans une minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Appel OFF
        try:
            response = requests.get(
                'https://world.openfoodfacts.org/cgi/search.pl',
                params={
                    'search_terms': q,
                    'json': 1,
                    'fields': 'product_name,nutriments,quantity',
                    'page_size': 5,
                },
                headers={'User-Agent': 'HestiaKitchen/1.0 (contact@hestia.app)'},
                timeout=5
            )
            data = response.json()
        except Exception:
            return Response({'error': 'OpenFoodFacts indisponible'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Formatage des résultats
        results = []
        for product in data.get('products', []):
            print(product)
            nutriments = product.get('nutriments', {})
            results.append({
                'nom': product.get('product_name', ''),
                'calories': nutriments.get('energy-kcal_100g'),
                'proteines': nutriments.get('proteins_100g'),
                'glucides': nutriments.get('carbohydrates_100g'),
                'lipides': nutriments.get('fat_100g'),
                'fibres': nutriments.get('fiber_100g'),
            })
        
        # Mise en cache 1 heure
        cache.set(cache_key, results, 60 * 60)

        return Response(results)
