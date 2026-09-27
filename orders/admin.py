from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'customer_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('code', 'customer_name', 'email', 'phone')
    readonly_fields = ('code', 'created_at', 'updated_at')
