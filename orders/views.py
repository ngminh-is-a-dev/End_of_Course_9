from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from cart.services import SESSION_KEY, VOUCHER_SESSION_KEY, cart_summary
from .models import Order
from .services import create_order


def checkout(request):
    summary = cart_summary(request.user, request.session)
    if not summary['items']:
        messages.info(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('products:list')
    if request.method == 'POST':
        required = ('name', 'phone', 'email', 'address', 'payment')
        if any(not request.POST.get(field, '').strip() for field in required):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin thanh toán.')
            return render(request, 'orders/checkout.html', summary)
        if request.POST.get('payment') != Order.COD:
            return HttpResponseBadRequest('Phương thức thanh toán không hợp lệ.')
        order = create_order(user=request.user, summary=summary, data=request.POST)
        request.session.pop(SESSION_KEY, None)
        request.session.pop(VOUCHER_SESSION_KEY, None)
        if order.voucher:
            order.voucher.is_used = True
            order.voucher.save(update_fields=['is_used'])
        return redirect('checkout-success', code=order.code)
    return render(request, 'orders/checkout.html', summary)


def success(request, code):
    order = get_object_or_404(Order, code=code)
    return render(request, 'orders/success.html', {'order': order})
