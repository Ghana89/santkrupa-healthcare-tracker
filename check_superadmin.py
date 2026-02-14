import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')
django.setup()

from hospital.models import User

# Check superadmin users
superadmins = User.objects.filter(role='super_admin')
print(f"Total superadmin users: {superadmins.count()}")
for user in superadmins:
    print(f"  - Username: {user.username}, Email: {user.email}, Is Active: {user.is_active}")

# Check all users
all_users = User.objects.all()
print(f"\nTotal users: {all_users.count()}")
for user in all_users[:10]:
    print(f"  - {user.username} ({user.role})")
