#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
django.setup()

from library.accounts.models import CustomUser

# Create a test user with known credentials
if not CustomUser.objects.filter(username='testuser').exists():
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='TestPassword123!',
        first_name='Test',
        last_name='User',
        role='MEMBER'
    )
    print(f"✓ Created test user: {user.username}")
else:
    print("✓ Test user already exists")

# List all users
users = CustomUser.objects.all()
print("\nAll users:")
for u in users:
    print(f"  - {u.username} ({u.email}) - Role: {u.role}")

print("\n--- Login Credentials ---")
print("Username: testuser")
print("Password: TestPassword123!")
