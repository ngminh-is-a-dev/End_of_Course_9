from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import LoginForm, SignupForm, UserProfileForm
from .models import UserProfile


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


@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Ảnh đại diện đã được cập nhật.')
            return redirect('accounts:profile')

    context = {
        'profile': user_profile,
        'form': form,
        'display_name': request.user.get_full_name().strip() or request.user.get_username(),
        'login_history': request.user.login_history.all()[:20],
        'orders': request.user.orders.prefetch_related('items'),
    }
    return render(request, 'accounts/profile.html', context)


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


class AccountLogoutView(LogoutView):
    next_page = 'home'
