import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('Admin@123456')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('✓ Admin password set to: Admin@123456')
except User.DoesNotExist:
    print('Admin user not found')
