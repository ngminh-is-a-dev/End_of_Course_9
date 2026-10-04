from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from .forms import LoginForm, SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Chào mừng bạn! Voucher miễn phí vận chuyển đã nằm trong tài khoản.')
        return redirect('cart:detail')
    return render(request, 'accounts/signup.html', {'form': form})


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


class AccountLogoutView(LogoutView):
    next_page = 'home'
