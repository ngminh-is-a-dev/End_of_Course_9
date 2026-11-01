from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.core.validators import validate_email
from cart.services import SESSION_KEY, VOUCHER_SESSION_KEY, cart_summary
from .models import Order
from .services import InsufficientStockError, VoucherUnavailableError, create_order


def checkout(request):
    summary = cart_summary(request.user, request.session)
    if not summary['items']:
        messages.info(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('products:list')
    if request.method == 'POST':
        required = ('name', 'phone', 'email', 'address', 'payment')
        data = {field: request.POST.get(field, '').strip() for field in required}
        if any(not data[field] for field in required):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin thanh toán.')
            return render(request, 'orders/checkout.html', summary)
        try:
            validate_email(data['email'])
        except ValidationError:
            messages.error(request, 'Email không hợp lệ.')
            return render(request, 'orders/checkout.html', summary)
        if len(data['name']) > 120 or len(data['phone']) > 30 or len(data['email']) > 254:
            messages.error(request, 'Thông tin giao hàng vượt quá độ dài cho phép.')
            return render(request, 'orders/checkout.html', summary)
        if data['payment'] != Order.COD:
            return HttpResponseBadRequest('Phương thức thanh toán không hợp lệ.')
        try:
            order = create_order(user=request.user, summary=summary, data=data)
        except InsufficientStockError:
            messages.error(request, 'Số lượng sản phẩm vượt quá tồn kho hiện tại. Vui lòng kiểm tra lại giỏ hàng.')
            return redirect('cart:detail')
        except VoucherUnavailableError:
            request.session.pop(VOUCHER_SESSION_KEY, None)
            messages.error(request, 'Voucher này vừa được sử dụng hoặc không còn hợp lệ. Vui lòng kiểm tra lại giỏ hàng.')
            return redirect('cart:detail')
        request.session.pop(SESSION_KEY, None)
        request.session.pop(VOUCHER_SESSION_KEY, None)
        return redirect('checkout-success', code=order.code)
    return render(request, 'orders/checkout.html', summary)


def success(request, code):
    order = get_object_or_404(Order, code=code)
    return render(request, 'orders/success.html', {'order': order})
