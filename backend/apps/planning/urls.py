from django.urls import path
from . import views

urlpatterns = [
    path('moments/', views.MomentListView.as_view(), name='moments'),
]