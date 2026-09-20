from django.urls import path
from .api_views import ProductApiDetailView, ProductApiListView

app_name = 'products-api'
urlpatterns = [
    path('products/', ProductApiListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductApiDetailView.as_view(), name='product-detail'),
]
