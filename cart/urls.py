from django.urls import path
from . import views
app_name = 'cart'
urlpatterns = [path('', views.cart_detail, name='detail'), path('add/<int:product_id>/', views.add_to_cart, name='add'), path('update/<int:product_id>/', views.update_cart, name='update'), path('voucher/apply/', views.apply_voucher, name='apply-voucher'), path('voucher/remove/', views.remove_voucher, name='remove-voucher')]
