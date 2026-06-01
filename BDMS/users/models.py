from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


ROLE_CHOICES = [
    ('ADMIN', 'Administrator'),
    ('USER', 'Regular User'),
]

DEPARTMENT_CHOICES = [
    ('HR', 'Human Resources'),
    ('FINANCE', 'Finance'),
    ('IT', 'Information Technology'),
    ('LEGAL', 'Legal'),
    ('ADMIN', 'Administration'),
    ('OPERATIONS', 'Operations'),
    ('PROCUREMENT', 'Procurement'),
    ('OTHER', 'Other'),
]


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Signal to automatically create user profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
