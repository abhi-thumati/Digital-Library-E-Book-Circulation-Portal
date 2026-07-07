from django.db import models
from django.urls import reverse

class Author(models.Model):
    name = models.CharField(
        max_length=200, 
        unique=True,
        help_text="Full name of the author."
    )
    biography = models.TextField(
        blank=True, 
        null=True,
        help_text="A short biographical sketch of the author."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('authors:author_detail', kwargs={'pk': self.pk})

    @property
    def book_count(self) -> int:
        """
        Dynamically calculate the count of books written by this author.
        Safely returns 0 if the Book model and relations do not exist yet.
        """
        try:
            return self.books.count()
        except AttributeError:
            return 0
