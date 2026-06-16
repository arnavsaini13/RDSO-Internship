"""
Utility functions for user operations
"""
from django.contrib.auth.models import User
from .models import UserProfile


def create_user_profile(user):
    """Create user profile when new user is created"""
    UserProfile.objects.get_or_create(user=user)


def get_user_role(user):
    """Get user role"""
    if user.is_superuser:
        return 'ADMIN'
    return 'USER'


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
