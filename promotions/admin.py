from django.contrib import admin
from .models import Voucher


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'voucher_type', 'is_used', 'created_at')
    list_filter = ('voucher_type', 'is_used')
    search_fields = ('code', 'user__username', 'user__email')

# Register your models here.
