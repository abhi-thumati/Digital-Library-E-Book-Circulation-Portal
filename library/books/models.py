from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
import re

def validate_isbn(value: str) -> None:
    """
    Validates that the provided ISBN is either a valid ISBN-10 or ISBN-13 format.
    Allows dashes and spaces.
    """
    cleaned = re.sub(r'[- ]', '', value)
    if len(cleaned) not in [10, 13]:
        raise ValidationError("ISBN must be exactly 10 or 13 characters (excluding dashes and spaces).")
    
    if len(cleaned) == 10:
        # 9 digits followed by a digit or X/x
        if not re.match(r'^\d{9}[\dX]$', cleaned, re.IGNORECASE):
            raise ValidationError("Invalid ISBN-10 format.")
    else:
        # 13 digits
        if not re.match(r'^\d{13}$', cleaned):
            raise ValidationError("Invalid ISBN-13 format.")

class Genre(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Name of the literary genre (e.g. Science Fiction, Biography)."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Short description of the genre."
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def __str__(self) -> str:
        return self.name

class Book(models.Model):
    title = models.CharField(
        max_length=255, 
        help_text="Title of the book."
    )
    authors = models.ManyToManyField(
        'authors.Author', 
        related_name='books',
        help_text="Authors who wrote this book."
    )
    genres = models.ManyToManyField(
        Genre, 
        related_name='books',
        help_text="Genres associated with this book."
    )
    isbn = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[validate_isbn],
        help_text="International Standard Book Number (10 or 13 digits)."
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Synopsys or summary of the book."
    )
    publication_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Date when the book was published."
    )
    publisher = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Name of the publisher."
    )
    cover_image = models.ImageField(
        upload_to='covers/', 
        blank=True, 
        null=True,
        help_text="Front cover image of the book."
    )
    total_copies = models.PositiveIntegerField(
        default=1,
        help_text="Total copies owned by the library."
    )
    available_copies = models.PositiveIntegerField(
        default=1,
        help_text="Copies currently on the shelf and available for borrowing."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
        ]

    def __str__(self) -> str:
        return f"{self.title} (ISBN: {self.isbn})"

    def get_absolute_url(self) -> str:
        return reverse('books:book_detail', kwargs={'pk': self.pk})

    def clean(self) -> None:
        super().clean()
        if self.available_copies > self.total_copies:
            raise ValidationError({
                'available_copies': "Available copies cannot exceed total copies."
            })

    def save(self, *args, **kwargs) -> None:
        # Standardize ISBN format by removing spaces and dashes, forcing uppercase
        self.isbn = re.sub(r'[- ]', '', self.isbn).upper()
        
        # If this is a new book, set available_copies to total_copies
        if not self.pk:
            self.available_copies = self.total_copies
            
        super().save(*args, **kwargs)
