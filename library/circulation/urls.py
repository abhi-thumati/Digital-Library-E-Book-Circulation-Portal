from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    # Librarian views
    path('active/', views.ActiveLoansListView.as_view(), name='active_loans'),
    path('overdue/', views.OverdueLoansListView.as_view(), name='overdue_loans'),
    path('issue/', views.IssueBookView.as_view(), name='issue_book'),
    path('return/<int:pk>/', views.ReturnBookView.as_view(), name='return_book'),
    path('pay-fine/<int:pk>/', views.PayFineView.as_view(), name='pay_fine'),
    
    # Member views
    path('history/', views.MemberBorrowingHistoryView.as_view(), name='member_history'),
    path('renew/<int:pk>/', views.RenewBookView.as_view(), name='renew_book'),
]
