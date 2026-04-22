from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from .models import ListeCourses, LigneCourses
from .serializers import ListeCoursesSerializer, LigneCourseSerializer
from apps.auth_foyer.models import MembreFoyer

def get_foyer(user):
    membre = MembreFoyer.objects.filter(user=user).select_related('foyer').first()
    return membre.foyer if membre else None

def get_or_create_liste_active(foyer):
    liste = ListeCourses.objects.filter(foyer=foyer, statut='active').first()
    if not liste:
        liste = ListeCourses.objects.create(foyer=foyer, statut='active')
    return liste

class ListeCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Shopping"], responses=ListeCoursesSerializer)
    def get(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        liste = get_or_create_liste_active(foyer)
        return Response(ListeCoursesSerializer(liste).data)

class LigneCoursesListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Shopping"], request=LigneCourseSerializer, responses=LigneCourseSerializer)
    def post(self, request):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        liste = get_or_create_liste_active(foyer)

        # Validation via un aliment ou un nom libre
        aliment = request.data.get('aliment')
        nom_libre = request.data.get('nom_libre')
        if not aliment and not nom_libre:
            return Response({'error': 'aliment ou nom_libre requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LigneCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(liste=liste, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LigneCoursesDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_ligne(self, pk, foyer):
        try:
            return LigneCourses.objects.get(pk=pk, liste__foyer=foyer)
        except ListeCourses.DoesNotExist:
            return None
    
    @extend_schema(tags=["Shopping"], request=LigneCourseSerializer, responses=LigneCourseSerializer)
    def patch(self, request, pk):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        
        ligne = self.get_ligne(pk, foyer)
        if not ligne:
            return Response({'errors':'Ligne introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LigneCourseSerializer(ligne, data=request.data, partial=True)
        if serializer.is_valid():
            if request.data.get('is_checked') and not ligne.is_checked:
                serializer.save(checked_at=timezone.now())
            elif not request.data.get('is_checked') and ligne.is_checked:
                serializer.save(checked_at=None)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(tags=["Shopping"], responses={204: None})
    def delete(self, request, pk):
        foyer = get_foyer(request.user)
        if not foyer:
            return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
        ligne = self.get_ligne(pk, foyer)
        if not ligne:
            return Response({'errors':'Ligne introuvable'}, status=status.HTTP_404_NOT_FOUND)
        ligne.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class FinCoursesView(APIView):
        permission_classes = [IsAuthenticated]

        @extend_schema(tags=["Shopping"], responses=LigneCourseSerializer)
        def post(self, request):
            foyer = get_foyer(request.user)
            if not foyer:
                return Response({'error': 'Aucun foyer'}, status=status.HTTP_404_NOT_FOUND)
            liste = get_or_create_liste_active(foyer)
            liste.lignes.filter(is_checked=True).delete()
            return Response(ListeCoursesSerializer(liste).data)