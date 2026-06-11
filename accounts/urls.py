from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, register, profile_view, CustomPasswordChangeView, dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/password/', CustomPasswordChangeView.as_view(), name='change_password'),
]
