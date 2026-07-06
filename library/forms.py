from django import forms
from django.core.exceptions import ValidationError
from .models import Book, Member, CirculationRecord
import re

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'member_id', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LIB-1001'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 99999 99999'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        cleaned_phone = re.sub(r'[\s\-()]', '', phone)
        if not cleaned_phone.replace('+', '').isdigit():
            raise ValidationError("Phone number must contain only digits, spaces, hyphens, or parentheses.")
        if len(cleaned_phone) < 10:
            raise ValidationError("Phone number is too short.")
        return phone

    def clean_member_id(self):
        member_id = self.cleaned_data.get('member_id')
        if not member_id.startswith('LIB-'):
            raise ValidationError("Member ID must start with prefix 'LIB-'.")
        return member_id

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'cover_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10 or 13 digit ISBN'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        clean_isbn = re.sub(r'[\s\-]', '', isbn)
        if not (len(clean_isbn) in [10, 13] and clean_isbn.isdigit()):
            raise ValidationError("ISBN must be a 10 or 13-digit numeric code.")
        
        qs = Book.objects.filter(isbn=isbn)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A book with this ISBN is already registered.")
        return isbn

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = CirculationRecord
        fields = ['book', 'member', 'issue_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select select-book'}),
            'member': forms.Select(attrs={'class': 'form-select select-member'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_issue_date'}),
        }

    def clean_book(self):
        book = self.cleaned_data.get('book')
        if book.available_copies <= 0:
            raise ValidationError(f"Unable to issue: '{book.title}' has no copies currently available.")
        return book

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        member = cleaned_data.get('member')
        
        if book and member:
            active_issue = CirculationRecord.objects.filter(book=book, member=member, is_returned=False)
            if active_issue.exists():
                raise ValidationError(f"Member '{member.name}' has already checked out an unreturned copy of '{book.title}'.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username...',
            'autofocus': 'autofocus'
        }),
        required=True,
        error_messages={'required': 'Username is required.'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password...',
            'id': 'password-field'
        }),
        required=True,
        error_messages={'required': 'Password is required.'}
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'rememberMe'
        })
    )
