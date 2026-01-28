import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')
django.setup()

from hospital.models import User

# Create admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@hospital.com',
        password='admin123',
        role='admin'
    )
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Admin user already exists!")
