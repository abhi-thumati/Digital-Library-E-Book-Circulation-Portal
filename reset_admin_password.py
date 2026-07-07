#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
django.setup()

from library.accounts.models import CustomUser

# Reset admin password to a known value
admin_user = CustomUser.objects.get(username='admin')
admin_user.set_password('Admin@123')
admin_user.save()

print("✓ Admin password reset successfully!")
print("\n--- Admin Login Credentials ---")
print("Username: admin")
print("Password: Admin@123")
print("Role: Administrator")
print("\nVisit: http://127.0.0.1:8000/accounts/login/")
