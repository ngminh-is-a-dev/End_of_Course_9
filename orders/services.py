from .models import Order, OrderItem


def create_order(*, user, summary, data):
    order = Order.objects.create(
        user=user if user.is_authenticated else None,
        customer_name=data['name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        subtotal=summary['subtotal'],
        shipping_fee=summary['shipping'],
        total=summary['total'],
        voucher=summary['voucher'],
        payment_method=data['payment'],
    )
    OrderItem.objects.bulk_create([
        OrderItem(order=order, product=item['product'], product_name=item['product'].name, unit_price=item['product'].price, quantity=item['quantity'])
        for item in summary['items']
    ])
    return order
