import uuid

from django.conf import settings
from django.db import models
from products.models import Product
from promotions.models import Voucher


class Order(models.Model):
    COD = 'cod'
    PAYMENT_METHODS = [(COD, 'Thanh toán khi nhận hàng')]

    PENDING = 'pending'
    PAID = 'paid'
    STATUS_CHOICES = [(PENDING, 'Chờ thanh toán'), (PAID, 'Đã thanh toán')]

    PACKING = 'packing'
    SHIPPING = 'shipping'
    DELIVERED = 'delivered'
    DELIVERY_STATUS_CHOICES = [
        (PACKING, 'Đang đóng gói'),
        (SHIPPING, 'Đang giao'),
        (DELIVERED, 'Đã giao'),
    ]

    code = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    subtotal = models.PositiveIntegerField()
    shipping_fee = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField()
    voucher = models.ForeignKey(
        Voucher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    delivery_status = models.CharField(max_length=12, choices=DELIVERY_STATUS_CHOICES, default=PACKING)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['code', 'payment_status'], name='order_code_status_idx')]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f'BL{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    class Meta:
        indexes = [models.Index(fields=['order', 'product'], name='order_item_product_idx')]
