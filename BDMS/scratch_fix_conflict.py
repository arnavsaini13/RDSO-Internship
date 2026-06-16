import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

print("Resolving email duplication conflicts...")

# 1. Update Arnav
u1 = User.objects.filter(email='8b.arnavsaini@gmail.com', profile__username='Arnav').first()
if u1:
    u1.email = 'arnav@example.com'
    u1.username = 'arnav@example.com'
    u1.save()
    u1.profile.email = 'arnav@example.com'
    u1.profile.save()
    print("[SUCCESS] Updated Arnav's email to 'arnav@example.com'")

# 2. Update Amit
u2 = User.objects.filter(email='8b.arnavsaini@gmail.com', profile__username='Amit').first()
if u2:
    u2.email = 'amit@example.com'
    u2.username = 'amit@example.com'
    u2.save()
    u2.profile.email = 'amit@example.com'
    u2.profile.save()
    print("[SUCCESS] Updated Amit's email to 'amit@example.com'")

# 3. Update Arnav Saini to be the unique owner of 8b.arnavsaini@gmail.com
u3 = User.objects.filter(username='Arnav Saini').first()
if u3:
    u3.username = '8b.arnavsaini@gmail.com'
    u3.save()
    u3.profile.email = '8b.arnavsaini@gmail.com'
    u3.profile.save()
    print("[SUCCESS] Set 'Arnav Saini' as the unique owner of '8b.arnavsaini@gmail.com'")

print("Conflict resolution complete.")
