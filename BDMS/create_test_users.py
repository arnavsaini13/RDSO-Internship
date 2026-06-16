import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

test_users = [
    {
        'username': 'admin',
        'password': 'Admin@123456',
        'first_name': 'Super',
        'last_name': 'Admin',
        'role': 'ADMIN',
        'department': 'ADMIN',
        'designation': 'System Administrator'
    },
    {
        'username': 'directorate',
        'password': 'User@123456',
        'first_name': 'Rajesh',
        'last_name': 'Kumar',
        'role': 'USER',
        'department': 'OPERATIONS',
        'designation': 'Senior Section Engineer'
    },
    {
        'username': 'scrutiny',
        'password': 'Scrutiny@123456',
        'first_name': 'Amit',
        'last_name': 'Sharma',
        'role': 'USER',
        'department': 'PROCUREMENT',
        'designation': 'Stores Officer'
    },
    {
        'username': 'manager',
        'password': 'Manager@123456',
        'first_name': 'Sanjay',
        'last_name': 'Singh',
        'role': 'ADMIN',
        'department': 'IT',
        'designation': 'Executive Director'
    }
]

print("Populating database with standardized role test accounts...")

for udata in test_users:
    email = f"{udata['username']}@rdso.railnet.gov.in"
    user, created = User.objects.get_or_create(username=email, defaults={'email': email})
    user.email = email
    user.set_password(udata['password'])
    user.first_name = udata['first_name']
    user.last_name = udata['last_name']
    if udata['role'] == 'ADMIN':
        user.is_staff = True
        user.is_superuser = True
    user.save()
    
    # Ensure profile matches
    profile, p_created = UserProfile.objects.get_or_create(user=user)
    profile.username = udata['username']
    profile.email = email
    profile.password = udata['password']
    profile.designation = udata['designation']
    profile.save()
    
    status = 'Created' if created else 'Updated'
    print(f"[SUCCESS] {status} User: {udata['username']} | Password: {udata['password']} | Role: {udata['role']} | Designation: {udata['designation']}")

print("\nDatabase populate complete. All role logins are active.")
