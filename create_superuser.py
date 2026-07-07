import os
import django
import sys

def main():
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
    django.setup()

    from library.accounts.models import CustomUser

    # Read credentials from env
    username = os.getenv('CREATE_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('CREATE_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('CREATE_SUPERUSER_PASSWORD', 'AdminPassword123')

    if not username or not password:
        print("Superuser setup skipped: CREATE_SUPERUSER_USERNAME or CREATE_SUPERUSER_PASSWORD not configured.")
        return

    try:
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            print(f"Superuser '{username}' exists. Recreating with new password...")
            CustomUser.objects.filter(username=username).delete()

        # Create fresh superuser
        print(f"Creating superuser '{username}'...")
        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        # Set admin role
        user.role = 'ADMIN'
        user.save()
        
        print(f"✓ Superuser '{username}' created successfully")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        
        # Verify authentication works
        from django.contrib.auth import authenticate
        test_user = authenticate(username=username, password=password)
        if test_user:
            print(f"✓ Authentication verified: Password works correctly")
        else:
            print(f"✗ Warning: Authentication verification failed")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
