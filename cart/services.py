from products.models import Product
from promotions.models import Voucher
SESSION_KEY = 'bean_leaf_cart'
VOUCHER_SESSION_KEY = 'bean_leaf_voucher'
DELIVERY_FEE = 30000


def get_cart(session): return session.get(SESSION_KEY, {})
def cart_count(session): return sum(get_cart(session).values())

def add_product(session, product_id, quantity=1):
    cart = get_cart(session); key = str(product_id); cart[key] = cart.get(key, 0) + quantity
    session[SESSION_KEY] = cart; session.modified = True

def set_quantity(session, product_id, quantity):
    cart = get_cart(session); key = str(product_id)
    if quantity > 0: cart[key] = quantity
    else: cart.pop(key, None)
    session[SESSION_KEY] = cart; session.modified = True

def cart_items(session):
    cart = get_cart(session); products = Product.objects.filter(id__in=cart.keys(), is_active=True).select_related('category')
    return [{'product': p, 'quantity': cart[str(p.id)], 'subtotal': p.price * cart[str(p.id)]} for p in products]


def get_voucher(user, session):
    code = session.get(VOUCHER_SESSION_KEY)
    if not code or not user.is_authenticated:
        return None
    return Voucher.objects.filter(user=user, code=code, is_used=False).first()


def available_voucher(user):
    if not user.is_authenticated:
        return None
    return user.vouchers.filter(voucher_type=Voucher.FREE_SHIPPING, is_used=False).first()


def cart_summary(user, session):
    items = cart_items(session)
    subtotal = sum(item['subtotal'] for item in items)
    voucher = get_voucher(user, session)
    shipping = 0 if voucher else (DELIVERY_FEE if subtotal else 0)
    return {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': subtotal + shipping,
        'voucher': voucher,
        'available_voucher': available_voucher(user),
    }
