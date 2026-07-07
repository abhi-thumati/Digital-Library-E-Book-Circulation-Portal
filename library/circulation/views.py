from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import Loan
from .forms import IssueBookForm
from library.books.models import Book
from library.dashboard.views import LibrarianRequiredMixin

def update_all_active_loans():
    """
    Helper function to run through active checked-out loans
    and recalculate overdue status/fines based on current date.
    """
    active_loans = Loan.objects.filter(return_date__isnull=True)
    for loan in active_loans:
        # Trigger save() which calls update_status_and_fine()
        loan.save()

class ActiveLoansListView(LibrarianRequiredMixin, ListView):
    model = Loan
    template_name = 'circulation/active_loans.html'
    context_object_name = 'loans'
    paginate_by = 15

    def get_queryset(self):
        update_all_active_loans()
        return Loan.objects.filter(return_date__isnull=True).select_related('borrower', 'book')


class OverdueLoansListView(LibrarianRequiredMixin, ListView):
    model = Loan
    template_name = 'circulation/overdue_loans.html'
    context_object_name = 'loans'
    paginate_by = 15

    def get_queryset(self):
        update_all_active_loans()
        return Loan.objects.filter(return_date__isnull=True, status='OVERDUE').select_related('borrower', 'book')


class IssueBookView(LibrarianRequiredMixin, CreateView):
    model = Loan
    form_class = IssueBookForm
    template_name = 'circulation/issue_book.html'
    success_url = reverse_lazy('circulation:active_loans')

    def get_initial(self):
        initial = super().get_initial()
        # Optionally pre-populate book if passed in URL query
        book_id = self.request.GET.get('book')
        if book_id:
            initial['book'] = book_id
        return initial

    def form_valid(self, form):
        loan = form.save(commit=False)
        book = loan.book
        
        # Decrement available copies
        book.available_copies = max(0, book.available_copies - 1)
        book.save()
        
        loan.status = 'BORROWED'
        loan.save()
        
        messages.success(
            self.request, 
            f"Book '{book.title}' has been successfully issued to '{loan.borrower.username}'."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to issue book. Please check form errors.")
        return super().form_invalid(form)


class ReturnBookView(LibrarianRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        loan = get_object_or_404(Loan, pk=pk, return_date__isnull=True)
        book = loan.book
        
        # Calculate final details
        today = date.today()
        loan.return_date = today
        loan.status = 'RETURNED'
        
        # Recalculate fine if overdue
        if today > loan.due_date:
            overdue_days = (today - loan.due_date).days
            loan.fine_amount = Decimal(overdue_days * 10)
        else:
            loan.fine_amount = Decimal('0.00')

        # If fine was generated, and it is 0, set fine_paid to True
        if loan.fine_amount == 0:
            loan.fine_paid = True
            
        loan.save()
        
        # Increment available copies
        book.available_copies = min(book.total_copies, book.available_copies + 1)
        book.save()
        
        if loan.fine_amount > 0:
            messages.warning(
                request, 
                f"Book '{book.title}' returned successfully. Late fine generated: ₹{loan.fine_amount}."
            )
        else:
            messages.success(request, f"Book '{book.title}' returned successfully.")
            
        return redirect('circulation:active_loans')


class PayFineView(LibrarianRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        loan = get_object_or_404(Loan, pk=pk)
        if loan.fine_amount > 0 and not loan.fine_paid:
            loan.fine_paid = True
            loan.save()
            messages.success(request, f"Fine of ₹{loan.fine_amount} for '{loan.book.title}' has been cleared.")
        else:
            messages.info(request, "No outstanding fines to pay for this loan.")
            
        # Redirect back to referring page or overdue list
        referrer = request.META.get('HTTP_REFERER')
        if referrer:
            return redirect(referrer)
        return redirect('circulation:overdue_loans')


class MemberBorrowingHistoryView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'circulation/member_history.html'
    context_object_name = 'loans'
    paginate_by = 10

    def get_queryset(self):
        # First update only the current member's active loans
        my_active = Loan.objects.filter(borrower=self.request.user, return_date__isnull=True)
        for loan in my_active:
            loan.save()
            
        return Loan.objects.filter(borrower=self.request.user).select_related('book')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Separate active and returned loans for display
        context['active_loans'] = Loan.objects.filter(
            borrower=self.request.user, 
            return_date__isnull=True
        ).select_related('book')
        context['returned_loans'] = Loan.objects.filter(
            borrower=self.request.user, 
            return_date__isnull=False
        ).select_related('book')
        return context


class RenewBookView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        loan = get_object_or_404(Loan, pk=pk, return_date__isnull=True)
        
        # Enforce security: only allow the borrowing member or a librarian to renew
        if not request.user.is_librarian_or_admin and loan.borrower != request.user:
            messages.error(request, "Permission denied.")
            return redirect('dashboard:member_dashboard')
            
        # Check renew count limits
        if loan.renew_count >= 1:
            messages.error(request, "Book cannot be renewed again. Max 1 renewal limit reached.")
        elif loan.status == 'OVERDUE':
            messages.error(request, "Overdue books cannot be renewed online. Please return the book first.")
        else:
            # Extend due date by 14 days
            loan.due_date = loan.due_date + timedelta(days=14)
            loan.renew_count += 1
            loan.save()
            messages.success(request, f"Borrowing for '{loan.book.title}' has been extended by 14 days.")
            
        referrer = request.META.get('HTTP_REFERER')
        if referrer:
            return redirect(referrer)
        return redirect('circulation:member_history')
