from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date

class Loan(models.Model):
    STATUS_CHOICES = (
        ('BORROWED', 'Borrowed'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
    )

    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans',
        help_text="The member who borrowed the book."
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.PROTECT,
        related_name='loans',
        help_text="The book that was borrowed."
    )
    borrow_date = models.DateField(
        default=timezone.now,
        help_text="Date when the book was checked out."
    )
    due_date = models.DateField(
        help_text="Due date for returning the book."
    )
    return_date = models.DateField(
        blank=True,
        null=True,
        help_text="Actual date when the book was returned."
    )
    renew_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this borrowing has been renewed."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='BORROWED',
        help_text="Status of the borrowing record."
    )
    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Fines calculated for returning the book late."
    )
    fine_paid = models.BooleanField(
        default=False,
        help_text="Designates if the outstanding fine has been paid."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-borrow_date']
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self) -> str:
        return f"{self.borrower.username} borrowed {self.book.title} (Status: {self.status})"

    @property
    def days_left(self) -> int:
        """
        Calculates how many days are left until the due date.
        Returns a negative number if the loan is overdue.
        """
        if self.return_date:
            return 0
        
        today = date.today()
        delta = self.due_date - today
        return delta.days

    def update_status_and_fine(self) -> None:
        """
        Calculates overdue fine based on ₹10 per day.
        Updates status to OVERDUE if the current date is past the due date and not returned.
        """
        if self.status == 'RETURNED':
            # If returned late, we keep the fine amount that was calculated at the time of return
            return

        today = date.today()
        if today > self.due_date:
            # Overdue
            overdue_days = (today - self.due_date).days
            self.fine_amount = float(overdue_days * 10)
            self.status = 'OVERDUE'
        else:
            self.fine_amount = 0.00
            self.status = 'BORROWED'

    def save(self, *args, **kwargs) -> None:
        # Dynamically set status/fine before saving if not returned
        if self.status != 'RETURNED':
            self.update_status_and_fine()
        super().save(*args, **kwargs)
