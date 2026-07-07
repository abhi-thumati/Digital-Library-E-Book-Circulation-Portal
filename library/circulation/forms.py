from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Loan
from library.books.models import Book

User = get_user_model()

class IssueBookForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['borrower', 'book', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'borrower': forms.Select(),
            'book': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['borrower', 'book']:
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            else:
                field.widget.attrs['class'] = 'form-select bg-dark text-white border-secondary'

        # Restrict borrower select list to only members (non-librarians/admins)
        self.fields['borrower'].queryset = User.objects.filter(role='MEMBER')
        
        # Restrict book select list to books with available copies
        # If modifying a loan (unlikely but just in case), show the current book too
        if self.instance and self.instance.pk:
            self.fields['book'].queryset = Book.objects.all()
        else:
            self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

        # Set default due date to 14 days from today
        default_due = timezone.now().date() + timedelta(days=14)
        self.fields['due_date'].initial = default_due

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        borrower = cleaned_data.get('borrower')
        due_date = cleaned_data.get('due_date')

        # Prevent checkout of books that are out of stock
        if book and book.available_copies <= 0:
            raise forms.ValidationError("The selected book is currently out of stock.")

        # Ensure due date is in the future
        if due_date and due_date <= timezone.now().date():
            raise forms.ValidationError("Due date must be a date in the future.")

        # Optional: prevent a member from borrowing the same book twice simultaneously
        if borrower and book:
            active_loans = Loan.objects.filter(borrower=borrower, book=book, return_date__isnull=True)
            if active_loans.exists():
                raise forms.ValidationError(f"{borrower.username} has already borrowed '{book.title}' and hasn't returned it yet.")

        return cleaned_data
