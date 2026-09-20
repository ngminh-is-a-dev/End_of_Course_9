from django.urls import path
from .views import AccountLoginView, AccountLogoutView, signup

app_name = 'accounts'
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', AccountLoginView.as_view(), name='login'),
    path('logout/', AccountLogoutView.as_view(), name='logout'),
]
