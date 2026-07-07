from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet, Q

from .models import Book, Genre
from .forms import BookForm, GenreForm
from library.dashboard.views import LibrarianRequiredMixin

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset().prefetch_related('authors', 'genres')
        
        # Search filter
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(isbn__icontains=query) |
                Q(authors__name__icontains=query) |
                Q(publisher__icontains=query)
            ).distinct()
            
        # Genre filter
        genre_id = self.request.GET.get('genre', '').strip()
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
            
        # Availability filter
        available_only = self.request.GET.get('available', '').strip() == 'true'
        if available_only:
            queryset = queryset.filter(available_copies__gt=0)
            
        # Sorting
        sort_by = self.request.GET.get('sort', 'title').strip()
        allowed_sorts = ['title', '-title', 'publication_date', '-publication_date', 'created_at', '-created_at']
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(sort_by)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['search_query'] = self.request.GET.get('q', '').strip()
        context['selected_genre'] = self.request.GET.get('genre', '').strip()
        context['available_only'] = self.request.GET.get('available', '').strip() == 'true'
        context['current_sort'] = self.request.GET.get('sort', 'title').strip()
        return context


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch circulation history or active loan if any
        # Check if the user has an active borrowing of this book
        user = self.request.user
        if user.is_authenticated:
            try:
                active_loan = self.object.loans.filter(borrower=user, return_date__isnull=True).first()
                context['active_loan'] = active_loan
            except AttributeError:
                context['active_loan'] = None
        return context


class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        # The save() method of Book automatically sets available_copies to total_copies
        messages.success(self.request, f"Book '{form.cleaned_data['title']}' has been cataloged successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to catalog book. Please review form details.")
        return super().form_invalid(form)


class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        # We need to calculate updated available copies if total copies changed
        book = form.save(commit=False)
        original_book = Book.objects.get(pk=book.pk)
        
        # Calculate how many copies are currently issued
        issued_copies = original_book.total_copies - original_book.available_copies
        
        # New available copies is new total minus currently issued copies
        book.available_copies = max(0, book.total_copies - issued_copies)
        book.save()
        form.save_m2m()
        
        messages.success(self.request, f"Book '{form.cleaned_data['title']}' has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update book. Please review form details.")
        return super().form_invalid(form)


class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        book_title = self.object.title
        # Prevent deleting a book that has active issues
        issued_count = self.object.total_copies - self.object.available_copies
        if issued_count > 0:
            messages.error(self.request, f"Cannot delete '{book_title}' because {issued_count} copy/copies are currently issued.")
            return self.render_to_response(self.get_context_data(form=form))

        messages.success(self.request, f"Book '{book_title}' has been deleted from the catalog.")
        return super().form_valid(form)


# Genre views (Librarians only)
class GenreListView(LibrarianRequiredMixin, ListView):
    model = Genre
    template_name = 'books/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 15


class GenreCreateView(LibrarianRequiredMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genre_list')

    def form_valid(self, form):
        messages.success(self.request, f"Genre '{form.cleaned_data['name']}' has been created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create genre. Correct errors below.")
        return super().form_invalid(form)


class GenreUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genre_list')

    def form_valid(self, form):
        messages.success(self.request, f"Genre '{form.cleaned_data['name']}' has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update genre. Correct errors below.")
        return super().form_invalid(form)


class GenreDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Genre
    template_name = 'books/genre_confirm_delete.html'
    success_url = reverse_lazy('books:genre_list')

    def form_valid(self, form):
        genre_name = self.object.name
        # Prevent deleting a genre if it contains books
        if self.object.books.exists():
            messages.error(self.request, f"Cannot delete genre '{genre_name}' because it contains associated books.")
            return self.render_to_response(self.get_context_data(form=form))

        messages.success(self.request, f"Genre '{genre_name}' has been deleted.")
        return super().form_valid(form)
