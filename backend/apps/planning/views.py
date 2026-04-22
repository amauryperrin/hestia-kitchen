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
from django.db.models import F


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

class RepasListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Planning"], responses=RepasSerializer(many=True))
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun Foyer'}, status=status.HTTP_404_NOT_FOUND)
        date = request.query_params.get('date')
        user_id = request.query_params.get('user_id')
        repas = Repas.objects.filter(user__memberships__foyer=foyer).select_related('moment', 'user')
        if date:
            repas = repas.filter(date=date)
        if user_id:
            repas = repas.filter(user__id=user_id)
        return Response(RepasSerializer(repas, many=True).data)

    @extend_schema(tags=["Planning"], request=RepasSerializer, responses=RepasSerializer)
    def post(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun Foyer'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RepasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LigneRepasListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Planning"], request=LigneRepasSerializer, responses=LigneRepasSerializer)
    def post(self, request, repas_id):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun Foyer'}, status=status.HTTP_404_NOT_FOUND)
        try:
            repas = Repas.objects.get(pk=repas_id, user=request.user)
        except Repas.DoesNotExist:
            return Response({'error': 'Repas Introuvable'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LigneRepasSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        aliment = serializer.validated_data['aliment']
        quantite = serializer.validated_data['quantite']

        # Calcul des snapshots macros
        ratio = quantite / aliment.quantite_reference
        calories_snapshot = aliment.calories * ratio
        proteines_snapshot = aliment.proteines * ratio
        glucides_snapshot = aliment.glucides * ratio
        lipides_snapshot = aliment.lipides * ratio
        fibres_snapshot = aliment.fibres * ratio

        # FIFO — consommation des lots par ordre d'ancienneté
        lots = Lot.objects.filter(
            foyer=foyer,
            aliment=aliment,
            quantite__gt=0
            ).order_by(F('date_peremption').asc(nulls_last=True))
        
        quantite_restante = quantite
        lot_peremption_snapshot = None
        prix_total = 0
        quantite_avec_prix = 0

        for lot in lots:
            if quantite_restante <= 0:
                break
            if lot_peremption_snapshot is None:
                lot_peremption_snapshot = lot.date_peremption
            
            consomme = min(lot.quantite, quantite_restante)
            
            if lot.prix_payer and lot.quantite > 0:
                prix_unitaire = lot.prix_payer / lot.quantite
                prix_total += prix_unitaire * consomme
                quantite_avec_prix += consomme
            
            lot.quantite -= consomme
            lot.save()
            quantite_restante -= consomme

        prix_snapshot = prix_total if quantite_avec_prix > 0 else None

        ligne = serializer.save(
            repas=repas,
            calories_snapshot=calories_snapshot,
            proteines_snapshot=proteines_snapshot,
            glucides_snapshot=glucides_snapshot,
            lipides_snapshot=lipides_snapshot,
            fibres_snapshot=fibres_snapshot,
            prix_snapshot=prix_snapshot,
            lot_peremption_snapshot=lot_peremption_snapshot,
        )

         # Mise à jour derniere_utilisation sur l'aliment
        from django.utils import timezone
        aliment.derniere_utilisation = timezone.now()
        aliment.save()
        
        return Response(LigneRepasSerializer(ligne).data, status=status.HTTP_201_CREATED)
    
class LigneRepasDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_ligne(self, pk, user):
        try:
            return LigneRepas.objects.get(pk=pk, repas__user=user)
        except LigneRepas.DoesNotExist:
            return None
    
    @extend_schema(tags=["Planning"], responses={204: None})
    def delete(self, request, pk):
        ligne = self.get_ligne(pk, request.user)
        if not ligne:
            return Response({'error':'Ligne introuvable'}, status=status.HTTP_404_NOT_FOUND)
        
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun Foyer'}, status=status.HTTP_404_NOT_FOUND)
        
        # Recréation d'un Lot avec la quantité de la ligne et date de péremption de la ligne
        Lot.objects.create(
            aliment=ligne.aliment,
            foyer=foyer,
            quantite=ligne.quantite,
            date_achat=ligne.repas.date,
            date_peremption=ligne.lot_peremption_snapshot,
            created_by=request.user
        )
        ligne.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)