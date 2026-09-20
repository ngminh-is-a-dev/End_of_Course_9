from django.conf import settings
from django.db import models


class Voucher(models.Model):
    FREE_SHIPPING = 'free_shipping'
    TYPE_CHOICES = [(FREE_SHIPPING, 'Miễn phí vận chuyển')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vouchers')
    code = models.CharField(max_length=40, unique=True)
    voucher_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=FREE_SHIPPING)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} — {self.user}'
