from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('foyer/', views.FoyerView.as_view(), name='foyer'),
    path('foyer/rejoindre/', views.RejoindreFoyerView.as_view(), name='rejoindre_foyer'),
    path('foyer/membres/', views.MembresFoyerView.as_view(), name='membres_foyer'),
]