from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Tên đăng nhập'}


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Tên đăng nhập')
