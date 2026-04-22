from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.ListeCoursesView.as_view(), name='liste_courses'),
    path('courses/lignes/', views.LigneCoursesListView.as_view(), name='lignes_courses'),
    path('courses/lignes/<int:pk>/', views.LigneCoursesDetailView.as_view(), name='ligne_courses_detail'),
    path('courses/fin/', views.FinCoursesView.as_view(), name='fin_courses'),
]