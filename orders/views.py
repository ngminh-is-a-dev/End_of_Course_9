import json
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from cart.services import SESSION_KEY, VOUCHER_SESSION_KEY, cart_summary
from .models import Order
from .services import create_order, mark_order_paid, sepay_checkout_data, sepay_checkout_url, verify_webhook


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
        payment = request.POST['payment']
        if payment not in (Order.COD, Order.SEPAY):
            return HttpResponseBadRequest('Phương thức thanh toán không hợp lệ.')
        if payment == Order.SEPAY and (not settings.SEPAY_GATEWAY_MERCHANT_ID or not settings.SEPAY_GATEWAY_SECRET_KEY):
            messages.error(request, 'SePay chưa được cấu hình. Vui lòng chọn COD hoặc cấu hình Merchant ID và Secret Key.')
            return render(request, 'orders/checkout.html', summary)
        order = create_order(user=request.user, summary=summary, data=request.POST)
        request.session.pop(SESSION_KEY, None)
        request.session.pop(VOUCHER_SESSION_KEY, None)
        if payment == Order.SEPAY:
            return redirect('sepay-payment', code=order.code)
        if order.voucher:
            order.voucher.is_used = True
            order.voucher.save(update_fields=['is_used'])
        return redirect('checkout-success', code=order.code)
    return render(request, 'orders/checkout.html', summary)


def sepay_payment(request, code):
    order = get_object_or_404(Order.objects.select_related('voucher'), code=code, payment_method=Order.SEPAY)
    if not settings.SEPAY_GATEWAY_MERCHANT_ID or not settings.SEPAY_GATEWAY_SECRET_KEY:
        messages.error(request, 'SePay chưa được cấu hình. Vui lòng thiết lập thông tin ngân hàng trong biến môi trường.')
        return redirect('cart:detail')
    return render(request, 'orders/sepay_payment.html', {
        'order': order,
        'gateway_url': sepay_checkout_url(),
        'gateway_fields': sepay_checkout_data(order),
    })


@require_GET
def sepay_payment_status(request, code):
    order = get_object_or_404(Order, code=code, payment_method=Order.SEPAY)
    return JsonResponse({'code': order.code, 'status': order.payment_status, 'paid': order.payment_status == Order.PAID})


@csrf_exempt
@require_POST
def sepay_webhook(request):
    if not verify_webhook(request):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    order = mark_order_paid(payload)
    if not order:
        return JsonResponse({'success': True, 'message': 'Ignored'})
    return JsonResponse({'success': True, 'code': order.code, 'status': order.payment_status})


def success(request, code):
    order = get_object_or_404(Order, code=code)
    return render(request, 'orders/success.html', {'order': order})
