#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
django.setup()

from library.accounts.models import CustomUser

# Check if johndoe was created
try:
    user = CustomUser.objects.get(username='johndoe')
    print(f"✓ User created successfully!")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Name: {user.first_name} {user.last_name}")
    print(f"  Role: {user.role}")
except CustomUser.DoesNotExist:
    print("✗ User not found")

print("\n--- All Users ---")
for u in CustomUser.objects.all():
    print(f"  - {u.username} ({u.email}) - {u.role}")
