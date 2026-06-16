import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

print("Starting synchronization of existing database users...")

for user in User.objects.all():
    old_username = user.username
    email = user.email
    
    # Check if the user has a profile, create one if not
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # 1. Ensure the profile's display username is populated
    if not profile.username:
        if email and old_username == email:
            # If the username is already the email, prefix before @ is a good fallback
            profile.username = email.split('@')[0]
        else:
            profile.username = old_username
        print(f"Set display username for {user.username} to '{profile.username}'")
    
    # 2. Ensure email field on profile is set
    if not profile.email and email:
        profile.email = email
        
    profile.save()
    
    # 3. Migrate the Django username to email under the hood if it is not already
    if email and old_username != email:
        # Check if another user already occupies this email as their username
        if not User.objects.filter(username=email).exclude(id=user.id).exists():
            user.username = email
            user.save()
            print(f"Migrated Django username: '{old_username}' -> '{email}'")
        else:
            print(f"[WARNING] Skipping Django username migrate for '{old_username}' to avoid duplicate '{email}'")

print("User synchronization complete.")
