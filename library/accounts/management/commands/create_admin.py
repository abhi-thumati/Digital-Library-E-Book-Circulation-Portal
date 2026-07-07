from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from library.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create or update admin superuser'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--password', type=str, default='Admin@123456', help='Admin password')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Admin email')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        # Delete existing admin if exists
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(f"Deleting existing admin user '{username}'...")
            CustomUser.objects.filter(username=username).delete()

        # Create new admin
        self.stdout.write(f"Creating admin user '{username}'...")
        admin = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        admin.role = 'ADMIN'
        admin.save()

        # Verify
        user = authenticate(username=username, password=password)
        if user:
            self.stdout.write(self.style.SUCCESS(f"✓ Admin user created successfully!"))
            self.stdout.write(f"  Username: {username}")
            self.stdout.write(f"  Password: {password}")
            self.stdout.write(f"  Email: {email}")
            self.stdout.write(f"  Role: ADMIN")
        else:
            self.stdout.write(self.style.ERROR(f"✗ Error: Authentication failed"))
