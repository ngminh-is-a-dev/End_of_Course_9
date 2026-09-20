from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'unit_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'customer_name', 'total', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('code', 'customer_name', 'email', 'phone', 'transaction_id')
    readonly_fields = ('code', 'subtotal', 'shipping_fee', 'total', 'transaction_id', 'paid_at', 'created_at')
    inlines = [OrderItemInline]
