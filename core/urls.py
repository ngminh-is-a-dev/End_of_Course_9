from django.urls import path
from . import views

urlpatterns = [path('', views.home, name='home'), path('<slug:page>/', views.content_page, name='content-page')]
