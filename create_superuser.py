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

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
        # Ensure it has the correct ADMIN role
        user = User.objects.get(username=username)
        if user.role != 'ADMIN':
            user.role = 'ADMIN'
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"Updated role of '{username}' to ADMIN.")
    else:
        print(f"Creating superuser '{username}'...")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='ADMIN'
        )
        print(f"Superuser '{username}' created successfully.")

if __name__ == '__main__':
    main()
