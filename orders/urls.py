from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<str:code>/', views.success, name='checkout-success'),
]
