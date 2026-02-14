import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')
django.setup()

from hospital.models import User

# Create superadmin user
username = 'superadmin'
email = 'superadmin@santkrupa.com'
password = 'SuperAdmin@123'

# Check if already exists
if User.objects.filter(username=username).exists():
    print(f"Superadmin user '{username}' already exists!")
else:
    superadmin = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='super_admin',
        is_active=True,
        is_staff=True,
        is_superuser=True
    )
    print(f"✓ Superadmin user created successfully!")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Role: super_admin")
