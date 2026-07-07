import os
import django
import sys

def main():
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryPortal.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Read credentials from env
    username = os.getenv('CREATE_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('CREATE_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('CREATE_SUPERUSER_PASSWORD', 'AdminPassword123')

    if not username or not password:
        print("Superuser setup skipped: CREATE_SUPERUSER_USERNAME or CREATE_SUPERUSER_PASSWORD not configured.")
        return

    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"Superuser '{username}' already exists. Updating...")
            user = User.objects.get(username=username)
            # Update password
            user.set_password(password)
            user.role = 'ADMIN'
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.save()
            print(f"✓ Updated admin user '{username}'")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Is Staff: {user.is_staff}")
            print(f"  Is Superuser: {user.is_superuser}")
        else:
            print(f"Creating superuser '{username}'...")
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # Set admin role after creation
            user.role = 'ADMIN'
            user.save()
            print(f"✓ Superuser '{username}' created successfully")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Is Staff: {user.is_staff}")
            print(f"  Is Superuser: {user.is_superuser}")
    except Exception as e:
        print(f"✗ Error creating/updating superuser: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
