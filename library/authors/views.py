from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet

from .models import Author
from .forms import AuthorForm
from library.dashboard.views import LibrarianRequiredMixin

class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    template_name = 'authors/author_list.html'
    context_object_name = 'authors'
    paginate_by = 10

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        
        # Search filter
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
            
        # Sorting
        sort_by = self.request.GET.get('sort', 'name').strip()
        allowed_sorts = ['name', '-name', 'created_at', '-created_at']
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(sort_by)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        context['current_sort'] = self.request.GET.get('sort', 'name').strip()
        return context


class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = 'authors/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch related books safely if books relation exists
        try:
            context['books'] = self.object.books.all()
        except AttributeError:
            context['books'] = []
        return context


class AuthorCreateView(LibrarianRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'authors/author_form.html'
    success_url = reverse_lazy('authors:author_list')

    def form_valid(self, form):
        messages.success(self.request, f"Author '{form.cleaned_data['name']}' has been created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create author. Please correct the errors below.")
        return super().form_invalid(form)


class AuthorUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'authors/author_form.html'
    success_url = reverse_lazy('authors:author_list')

    def form_valid(self, form):
        messages.success(self.request, f"Author '{form.cleaned_data['name']}' has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update author. Please correct the errors below.")
        return super().form_invalid(form)


class AuthorDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Author
    template_name = 'authors/author_confirm_delete.html'
    success_url = reverse_lazy('authors:author_list')

    def form_valid(self, form):
        author_name = self.object.name
        # Prevent deletion if author has books (in future phase)
        try:
            if self.object.books.exists():
                messages.error(self.request, f"Cannot delete '{author_name}' because they are associated with existing books.")
                return self.render_to_response(self.get_context_data(form=form))
        except AttributeError:
            pass

        messages.success(self.request, f"Author '{author_name}' has been deleted successfully.")
        return super().form_valid(form)
