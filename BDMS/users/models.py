from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    password = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_temp_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.username} - {self.email}"

    @property
    def role(self):
        return 'ADMIN' if self.user.is_superuser else 'USER'

    @property
    def get_role_display(self):
        return 'Administrator' if self.user.is_superuser else 'Regular User'


# Signal to automatically create user profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return
    if created:
        UserProfile.objects.get_or_create(user=instance)
