from django.contrib import admin
from .models import Book, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'total_copies', 'available_copies', 'publication_date')
    list_filter = ('genres', 'publication_date')
    search_fields = ('title', 'isbn', 'publisher')
    filter_horizontal = ('authors', 'genres')
