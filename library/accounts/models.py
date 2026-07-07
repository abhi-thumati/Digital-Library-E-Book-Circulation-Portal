from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('LIBRARIAN', 'Librarian'),
        ('MEMBER', 'Member'),
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='MEMBER',
        help_text="Designates the role of the user inside the portal."
    )
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        help_text="Profile picture or photo of the user."
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Contact phone number."
    )
    address = models.TextField(
        blank=True, 
        null=True,
        help_text="Residential or correspondence address."
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self) -> bool:
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_librarian_or_admin(self) -> bool:
        return self.role in ['ADMIN', 'LIBRARIAN'] or self.is_superuser

    @property
    def is_member(self) -> bool:
        return self.role == 'MEMBER'
