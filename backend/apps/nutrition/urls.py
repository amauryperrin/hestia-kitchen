from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategorieListView.as_view(), name='categories'),
    path('aliments/', views.AlimentListView.as_view(), name='aliments'),
    path('aliments/<int:pk>/', views.AlimentDetailView.as_view(), name='aliment_detail')
]