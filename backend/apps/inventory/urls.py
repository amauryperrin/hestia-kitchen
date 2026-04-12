from django.urls import path
from . import views

urlpatterns = [
    path('lots/', views.LotListView.as_view(), name='lots'),
    path('lots/<int:pk>/', views.LotDetailView.as_view(), name='lot_detail'),
    path('stock/', views.StockAlimentView.as_view(), name='stock'),
]

