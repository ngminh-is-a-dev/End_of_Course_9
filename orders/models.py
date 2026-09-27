import uuid
from django.conf import settings
from django.db import models


class Order(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [(PENDING, 'Chờ xử lý'), (CONFIRMED, 'Đã xác nhận'), (COMPLETED, 'Hoàn thành'), (CANCELLED, 'Đã hủy')]

    code = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    customer_name = models.CharField('Tên khách hàng', max_length=120)
    email = models.EmailField('Email')
    phone = models.CharField('Số điện thoại', max_length=30)
    address = models.TextField('Địa chỉ giao hàng')
    total = models.PositiveIntegerField('Tổng tiền (VNĐ)', default=0)
    status = models.CharField('Trạng thái', max_length=12, choices=STATUS_CHOICES, default=PENDING)
    note = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật lần cuối', auto_now=True)

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['code', 'status'], name='order_code_status_idx')]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f'BL{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
