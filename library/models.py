# pyrefly: ignore [missing-import]
from django.db import models  # pyrefly: ignore [missing-import]
from django.utils import timezone  # pyrefly: ignore [missing-import]
from datetime import timedelta, date
from decimal import Decimal
from django.core.exceptions import ValidationError  # pyrefly: ignore [missing-import]

class Author(models.Model):
    name = models.CharField(max_length=255)
    biography = models.TextField()

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_url = models.URLField(max_length=500, blank=True, null=True)

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Member(models.Model):
    name = models.CharField(max_length=255)
    member_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    joined_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.name} ({self.member_id})"

class CirculationRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='circulation_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='circulation_records')
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField(blank=True)
    return_date = models.DateField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    is_returned = models.BooleanField(default=False)

    def calculate_fine(self):
        """Calculates outstanding fine if returned late or overdue, ₹50 per day."""
        fine_per_day = Decimal('50.00')
        end_date = self.return_date if self.is_returned else date.today()
        
        if end_date > self.due_date:
            days_overdue = (end_date - self.due_date).days
            return Decimal(days_overdue) * fine_per_day
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)
        
        self.fine_amount = self.calculate_fine()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} issued to {self.member.name} (Due: {self.due_date})"
