from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # /profile/me/ resolves the logged-in user's own username and redirects —
    # used as LOGIN_REDIRECT_URL so we never hardcode a username at login time.
    path('profile/me/', views.profile_detail_self, name='profile_detail_self'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
]
