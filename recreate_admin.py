#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
django.setup()

from library.accounts.models import CustomUser

# Delete existing admin user if exists
CustomUser.objects.filter(username='admin').delete()
print("Deleted old admin user if it existed")

# Create fresh admin user
admin = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='Admin@123456'
)

# Set role
admin.role = 'ADMIN'
admin.save()

print("✓ Admin user created successfully!")
print(f"  Username: admin")
print(f"  Password: Admin@123456")
print(f"  Email: admin@example.com")
print(f"  Role: ADMIN")

# Verify
from django.contrib.auth import authenticate
user = authenticate(username='admin', password='Admin@123456')
if user:
    print(f"\n✓ Authentication verification: SUCCESS")
else:
    print(f"\n✗ Authentication verification: FAILED")
