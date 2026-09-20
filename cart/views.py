from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .services import VOUCHER_SESSION_KEY, add_product, cart_summary, set_quantity

def cart_detail(request):
    return render(request, 'cart/detail.html', cart_summary(request.user, request.session))

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if request.method == 'POST':
        add_product(request.session, product.id, max(1, int(request.POST.get('quantity', 1))))
        messages.success(request, f'Đã thêm {product.name} vào giỏ hàng.')
    return redirect(request.POST.get('next', 'cart:detail'))

def update_cart(request, product_id):
    if request.method == 'POST': set_quantity(request.session, product_id, max(0, int(request.POST.get('quantity', 0))))
    return redirect('cart:detail')


def apply_voucher(request):
    if request.method != 'POST':
        return redirect('cart:detail')
    if not request.user.is_authenticated:
        messages.info(request, 'Hãy đăng ký hoặc đăng nhập để nhận voucher miễn phí vận chuyển.')
        return redirect('accounts:signup')
    voucher = request.user.vouchers.filter(code=request.POST.get('code', '').strip().upper(), is_used=False).first()
    if voucher:
        request.session[VOUCHER_SESSION_KEY] = voucher.code
        request.session.modified = True
        messages.success(request, f'Đã áp dụng voucher {voucher.code}: miễn phí vận chuyển.')
    else:
        messages.error(request, 'Voucher không hợp lệ hoặc đã được sử dụng.')
    return redirect('cart:detail')


def remove_voucher(request):
    if request.method == 'POST':
        request.session.pop(VOUCHER_SESSION_KEY, None)
        request.session.modified = True
        messages.info(request, 'Đã gỡ voucher khỏi đơn hàng.')
    return redirect('cart:detail')

# Create your views here.
