#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
django.setup()

from library.accounts.models import CustomUser
from django.contrib.auth import authenticate

# Check admin user
try:
    admin = CustomUser.objects.get(username='admin')
    print(f"Admin user found:")
    print(f"  Username: {admin.username}")
    print(f"  Email: {admin.email}")
    print(f"  Role: {admin.role}")
    print(f"  Is Staff: {admin.is_staff}")
    print(f"  Is Superuser: {admin.is_superuser}")
    print(f"  Password hash: {admin.password[:20]}...")
    
    # Try to authenticate
    print("\nTesting authentication:")
    user = authenticate(username='admin', password='Admin@123456')
    if user is not None:
        print(f"✓ Authentication successful!")
    else:
        print(f"✗ Authentication failed!")
        
        # Try with check_password
        print(f"\nTrying check_password method:")
        if admin.check_password('Admin@123456'):
            print(f"✓ Password matches!")
        else:
            print(f"✗ Password does not match!")
            print(f"\nLet's check the user info more carefully:")
            print(f"  is_active: {admin.is_active}")
            
except CustomUser.DoesNotExist:
    print("Admin user not found!")
