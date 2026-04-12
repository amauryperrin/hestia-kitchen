from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Moment, Repas, LigneRepas
from .serializers import MomentSerializer, LigneRepasSerializer, RepasSerializer
from apps.auth_foyer.models import MembreFoyer
from apps.nutrition.models import Aliment
from apps.inventory.models import Lot


def get_foyer(user):
    membre = MembreFoyer.objects.filter(user=user).select_related('foyer').first()
    return membre.foyer if membre else None

class MomentListView(APIView):
    permissions_classes = [IsAuthenticated]
    
    @extend_schema(tags=["Planning"], responses=MomentSerializer(many=True))
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        moments = Moment.objects.filter(foyer=foyer)
        return Response(MomentSerializer(moments, many=True).data)
    
    @extend_schema(tags=["Planning"], request=MomentSerializer, responses=MomentSerializer)
    def post(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MomentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(foyer=foyer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
