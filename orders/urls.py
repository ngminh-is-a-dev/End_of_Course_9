from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<str:code>/', views.success, name='checkout-success'),
    path('sepay/<str:code>/', views.sepay_payment, name='sepay-payment'),
    path('sepay/<str:code>/error/', views.sepay_payment, name='sepay-payment-error'),
    path('sepay/<str:code>/cancel/', views.sepay_payment, name='sepay-payment-cancel'),
    path('sepay/<str:code>/status/', views.sepay_payment_status, name='sepay-payment-status'),
    path('webhooks/sepay/', views.sepay_webhook, name='sepay-webhook'),
]
