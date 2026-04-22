from django.urls import path
from . import views

urlpatterns = [
    path('moments/', views.MomentListView.as_view(), name='moments'),
    path('repas/', views.RepasListView.as_view(), name='repas'),
    path('repas/<int:repas_id>/lignes/', views.LigneRepasListView.as_view(), name='lignes_repas'),

]