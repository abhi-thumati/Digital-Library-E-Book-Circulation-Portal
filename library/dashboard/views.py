from django.views.generic import TemplateView
from django.views import View
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from library.books.models import Book
from library.circulation.models import Loan
from .reports_helper import generate_excel_report, generate_pdf_report

User = get_user_model()

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_librarian_or_admin

class MemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_member

class AdminDashboardView(LibrarianRequiredMixin, TemplateView):
    template_name = 'dashboard/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure overdue status/fines are up to date
        from library.circulation.views import update_all_active_loans
        update_all_active_loans()
        
        # Calculate stats
        total_books = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
        available_books = Book.objects.aggregate(avail=Sum('available_copies'))['avail'] or 0
        issued_books = Loan.objects.filter(return_date__isnull=True).count()
        total_members = User.objects.filter(role='MEMBER').count()
        
        today_issues = Loan.objects.filter(borrow_date=date.today()).count()
        today_returns = Loan.objects.filter(return_date=date.today()).count()
        overdue_books = Loan.objects.filter(return_date__isnull=True, status='OVERDUE').count()
        
        # Outstanding unpaid fines
        total_fine = Loan.objects.filter(fine_paid=False).aggregate(total=Sum('fine_amount'))['total'] or 0.0
        
        # Recent activities (checkout, check-in, registration, book cataloging)
        recent_activities = []
        recent_loans = Loan.objects.all().select_related('borrower', 'book').order_by('-updated_at')[:5]
        for loan in recent_loans:
            if loan.status == 'RETURNED':
                desc = f"Member @{loan.borrower.username} returned '{loan.book.title}'"
            elif loan.status == 'OVERDUE':
                desc = f"Book '{loan.book.title}' is overdue for @{loan.borrower.username}"
            else:
                desc = f"Book '{loan.book.title}' issued to @{loan.borrower.username}"
            
            recent_activities.append({
                'description': desc,
                'timestamp': loan.updated_at
            })
            
        context.update({
            'total_books': total_books,
            'available_books': available_books,
            'issued_books': issued_books,
            'total_members': total_members,
            'today_issues': today_issues,
            'today_returns': today_returns,
            'overdue_books': overdue_books,
            'total_fine': float(total_fine),
            'recent_activities': recent_activities
        })
        return context

class MemberDashboardView(MemberRequiredMixin, TemplateView):
    template_name = 'dashboard/member.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Update user's active loans
        my_active_loans = Loan.objects.filter(borrower=user, return_date__isnull=True).select_related('book')
        for loan in my_active_loans:
            loan.save()
            
        # Stats
        borrowed_books_count = my_active_loans.count()
        history_count = Loan.objects.filter(borrower=user, return_date__isnull=False).count()
        
        # Outstanding fines
        fine_amount = Loan.objects.filter(borrower=user, fine_paid=False).aggregate(total=Sum('fine_amount'))['total'] or 0.0
        
        # Upcoming dues in next 3 days
        upcoming_dues = []
        three_days_from_now = date.today() + timedelta(days=3)
        near_dues = my_active_loans.filter(due_date__lte=three_days_from_now)
        for loan in near_dues:
            upcoming_dues.append({
                'title': loan.book.title,
                'days_left': loan.days_left
            })
            
        # Formatted borrowed books list
        borrowed_books = []
        for loan in my_active_loans:
            borrowed_books.append({
                'pk': loan.pk,
                'title': loan.book.title,
                'borrowed_date': loan.borrow_date,
                'due_date': loan.due_date,
                'days_left': loan.days_left
            })
            
        # Book recommendations (latest 3 books in system that the user hasn't borrowed yet)
        borrowed_book_ids = Loan.objects.filter(borrower=user).values_list('book_id', flat=True)
        recommended_query = Book.objects.exclude(id__in=borrowed_book_ids).prefetch_related('authors').order_by('-created_at')[:3]
        recommended_books = []
        for book in recommended_query:
            authors_str = ", ".join([a.name for a in book.authors.all()])
            recommended_books.append({
                'title': book.title,
                'author': authors_str if authors_str else "Unknown Author"
            })
            
        context.update({
            'borrowed_books_count': borrowed_books_count,
            'history_count': history_count,
            'fine_amount': float(fine_amount),
            'active_reservations': 0,
            'upcoming_dues': upcoming_dues,
            'borrowed_books': borrowed_books,
            'recommended_books': recommended_books
        })
        return context


class PortalReportsView(LibrarianRequiredMixin, TemplateView):
    template_name = 'dashboard/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure overdue status/fines are up to date
        from library.circulation.views import update_all_active_loans
        update_all_active_loans()
        
        from library.books.models import Genre
        total_books = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
        total_genres = Genre.objects.count()
        active_loans_count = Loan.objects.filter(return_date__isnull=True).count()
        overdue_loans_count = Loan.objects.filter(return_date__isnull=True, status='OVERDUE').count()
        total_unpaid_fines = Loan.objects.filter(fine_paid=False).aggregate(total=Sum('fine_amount'))['total'] or 0.0
        
        context.update({
            'total_books': total_books,
            'total_genres': total_genres,
            'active_loans_count': active_loans_count,
            'overdue_loans_count': overdue_loans_count,
            'total_unpaid_fines': float(total_unpaid_fines),
        })
        return context

class ExportReportView(LibrarianRequiredMixin, View):
    def get(self, request, report_type, format_type, *args, **kwargs):
        if report_type not in ['books', 'loans', 'fines']:
            raise Http404("Report type not found")
        if format_type not in ['excel', 'pdf']:
            raise Http404("Format not found")
            
        # Ensure overdue status/fines are up to date
        from library.circulation.views import update_all_active_loans
        update_all_active_loans()
        
        if report_type == 'books':
            queryset = Book.objects.all().prefetch_related('authors', 'genres')
        elif report_type == 'loans':
            queryset = Loan.objects.filter(return_date__isnull=True).select_related('borrower', 'book')
        elif report_type == 'fines':
            queryset = Loan.objects.filter(fine_amount__gt=0).select_related('borrower', 'book')
            
        if format_type == 'excel':
            return generate_excel_report(report_type, queryset)
        else:
            return generate_pdf_report(report_type, queryset)
