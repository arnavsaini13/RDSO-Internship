from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('verify-link/<str:token>/', views.verify_link_view, name='verify_link'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('change-password-popup/', views.change_password_popup_view, name='change_password_popup'),
    path('captcha/', views.generate_captcha_view, name='captcha'),
]
