from django.db import transaction
from django.db.models import F
from cart.services import DELIVERY_FEE
from .models import Order, OrderItem
from products.models import Product
from promotions.models import Voucher


class InsufficientStockError(Exception):
    pass


class VoucherUnavailableError(Exception):
    pass


@transaction.atomic
def create_order(*, user, summary, data):
    requested_items = summary['items']
    product_ids = [item['product'].pk for item in requested_items]
    locked_products = Product.objects.select_for_update().filter(
        pk__in=product_ids,
        is_active=True,
    ).in_bulk()

    items = []
    subtotal = 0
    for requested in requested_items:
        product = locked_products.get(requested['product'].pk)
        quantity = requested['quantity']
        if product is None or product.stock < quantity:
            raise InsufficientStockError
        subtotal += product.price * quantity
        items.append((product, quantity))

    voucher = summary['voucher']
    if voucher:
        voucher = Voucher.objects.select_for_update().filter(
            pk=voucher.pk,
            user=user,
            is_used=False,
        ).first()
        if voucher is None:
            raise VoucherUnavailableError

    shipping_fee = 0 if voucher else (DELIVERY_FEE if subtotal else 0)
    order = Order.objects.create(
        user=user if user.is_authenticated else None,
        customer_name=data['name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total=subtotal + shipping_fee,
        voucher=voucher,
        payment_method=data['payment'],
    )
    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
        )
        for product, quantity in items
    ])

    for product, quantity in items:
        updated = Product.objects.filter(
            pk=product.pk,
            is_active=True,
            stock__gte=quantity,
        ).update(stock=F('stock') - quantity)
        if updated != 1:
            raise InsufficientStockError

    if voucher:
        updated = Voucher.objects.filter(pk=voucher.pk, is_used=False).update(is_used=True)
        if updated != 1:
            raise VoucherUnavailableError
    return order
