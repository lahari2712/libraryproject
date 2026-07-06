from django.shortcuts import render, redirect, get_object_or_404  # pyrefly: ignore [missing-import]
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View  # pyrefly: ignore [missing-import]
from django.contrib.auth.mixins import LoginRequiredMixin  # pyrefly: ignore [missing-import]
from django.contrib.auth import authenticate, login, logout  # pyrefly: ignore [missing-import]
from django.contrib import messages  # pyrefly: ignore [missing-import]
from django.db.models import Q, Sum, Count, F  # pyrefly: ignore [missing-import]
from django.db import transaction  # pyrefly: ignore [missing-import]
from decimal import Decimal
from datetime import date
from .models import Author, Book, Member, CirculationRecord
from .forms import BookIssueForm, MemberForm, LoginForm

# Custom mixin to enforce staff/admin check
class StaffRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Access denied. Administrator privileges are required to access this resource.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

# Dashboard View
class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        context['total_books'] = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
        context['total_book_titles'] = Book.objects.count()
        context['total_authors'] = Author.objects.count()
        context['total_members'] = Member.objects.count()
        context['books_issued'] = CirculationRecord.objects.filter(is_returned=False).count()
        context['available_books'] = Book.objects.aggregate(available=Sum('available_copies'))['available'] or 0
        context['overdue_books'] = CirculationRecord.objects.filter(is_returned=False, due_date__lt=today).count()
        context['total_fines_collected'] = CirculationRecord.objects.filter(is_returned=True).aggregate(fines=Sum('fine_amount'))['fines'] or Decimal('0.00')

        # Embedded Catalog Section with dynamic filtering (matching screenshot)
        queryset = Book.objects.select_related('author').all().order_by('title')
        search_query = self.request.GET.get('search', '').strip()
        genre_filter = self.request.GET.get('genre', '').strip()
        availability_filter = self.request.GET.get('availability', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
        if genre_filter:
            queryset = queryset.filter(genre__iexact=genre_filter)
        
        if availability_filter == 'available':
            queryset = queryset.filter(available_copies__gt=2)
        elif availability_filter == 'lowstock':
            queryset = queryset.filter(available_copies__gt=0, available_copies__lte=2)
        elif availability_filter == 'outofstock':
            queryset = queryset.filter(available_copies=0)
        elif availability_filter == 'issued':
            queryset = queryset.filter(available_copies__lt=F('total_copies'))

        context['books'] = queryset[:6]
        context['genres'] = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')
        context['selected_genre'] = genre_filter
        context['selected_availability'] = availability_filter
        context['search_query'] = search_query

        # Charts Data
        genre_data = Book.objects.values('genre').annotate(count=Count('id')).order_by('genre')
        context['genres_list'] = [item['genre'] for item in genre_data]
        context['genre_counts'] = [item['count'] for item in genre_data]

        context['out_of_stock'] = Book.objects.filter(available_copies=0).count()
        context['low_stock'] = Book.objects.filter(available_copies__gt=0, available_copies__lte=2).count()
        context['in_stock'] = Book.objects.filter(available_copies__gt=2).count()

        monthly_data = CirculationRecord.objects.values('issue_date__month').annotate(count=Count('id')).order_by('issue_date__month')
        months_lookup = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        context['months'] = []
        context['monthly_issues'] = []
        for item in monthly_data:
            m_num = item['issue_date__month']
            if m_num is not None:
                context['months'].append(months_lookup[m_num - 1])
                context['monthly_issues'].append(item['count'])

        # Bottom widgets lists
        context['recent_issues'] = CirculationRecord.objects.select_related('book', 'member').order_by('-issue_date')[:3]
        context['overdue_records_list'] = CirculationRecord.objects.select_related('book', 'member').filter(is_returned=False, due_date__lt=today).order_by('due_date')[:3]
        context['today'] = today

        return context

# Book Catalog view (AJAX enabled for dynamic instant filtering)
class BookCatalogView(ListView):
    model = Book
    template_name = 'catalog.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.select_related('author').all().order_by('title')
        search_query = self.request.GET.get('search', '').strip()
        genre_filter = self.request.GET.get('genre', '').strip()
        availability_filter = self.request.GET.get('availability', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
        if genre_filter:
            queryset = queryset.filter(genre__iexact=genre_filter)

        if availability_filter == 'available':
            queryset = queryset.filter(available_copies__gt=2)
        elif availability_filter == 'lowstock':
            queryset = queryset.filter(available_copies__gt=0, available_copies__lte=2)
        elif availability_filter == 'outofstock':
            queryset = queryset.filter(available_copies=0)
        elif availability_filter == 'issued':
            queryset = queryset.filter(available_copies__lt=F('total_copies'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')
        context['selected_genre'] = self.request.GET.get('genre', '')
        context['selected_availability'] = self.request.GET.get('availability', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(self.request, 'catalog_partial.html', context)
        return super().render_to_response(context, **response_kwargs)

class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['circulation_history'] = CirculationRecord.objects.filter(book=self.object).select_related('member').order_by('-issue_date')[:10]
        return context

# Book Issue view
class BookIssueView(StaffRequiredMixin, View):
    template_name = 'issue_book.html'

    def get(self, request):
        form = BookIssueForm()
        book_id = request.GET.get('book')
        if book_id:
            form.fields['book'].initial = book_id
        form.fields['issue_date'].initial = date.today().strftime('%Y-%m-%d')
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = BookIssueForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    record = form.save(commit=False)
                    book = record.book
                    
                    if book.available_copies <= 0:
                        form.add_error('book', "No available copies in catalog.")
                        return render(request, self.template_name, {'form': form})
                        
                    book.available_copies -= 1
                    book.save()
                    record.save()
                    
                    messages.success(request, f"Checked out '{book.title}' to {record.member.name}. Due on {record.due_date.strftime('%d-%b-%Y')}.")
                    return redirect('catalog')
            except Exception as e:
                form.add_error(None, f"Database transaction failed: {str(e)}")
        
        return render(request, self.template_name, {'form': form})

# Book Return view
class BookReturnView(StaffRequiredMixin, View):
    template_name = 'return_book.html'

    def get(self, request, pk):
        record = get_object_or_404(CirculationRecord.objects.select_related('book', 'member'), pk=pk, is_returned=False)
        today = date.today()
        fine = Decimal('0.00')
        overdue_days = 0
        if today > record.due_date:
            overdue_days = (today - record.due_date).days
            fine = Decimal(overdue_days) * Decimal('50.00')

        return render(request, self.template_name, {
            'record': record,
            'overdue_days': overdue_days,
            'calculated_fine': fine,
            'today': today
        })

    def post(self, request, pk):
        record = get_object_or_404(CirculationRecord, pk=pk, is_returned=False)
        today = date.today()
        
        try:
            with transaction.atomic():
                record.return_date = today
                record.is_returned = True
                record.save()  # Auto updates fine amount in model save
                
                book = record.book
                book.available_copies += 1
                book.save()
                
                fine_msg = f" Outstanding fine: ₹{record.fine_amount} collected." if record.fine_amount > 0 else " Book returned in-time (no fine)."
                messages.success(request, f"Book '{book.title}' returned by {record.member.name}.{fine_msg}")
                return redirect('history')
        except Exception as e:
            messages.error(request, f"Error processing return action: {str(e)}")
            return redirect('history')

# History view
class MemberHistoryView(LoginRequiredMixin, ListView):
    model = CirculationRecord
    template_name = 'history.html'
    context_object_name = 'records'
    paginate_by = 15

    def get_queryset(self):
        queryset = CirculationRecord.objects.select_related('book', 'member').all().order_by('-issue_date')
        member_id = self.request.GET.get('member_id', '').strip()
        status = self.request.GET.get('status', '').strip()
        
        if member_id:
            queryset = queryset.filter(Q(member__member_id__iexact=member_id) | Q(member__name__icontains=member_id))
        if status == 'active':
            queryset = queryset.filter(is_returned=False)
        elif status == 'returned':
            queryset = queryset.filter(is_returned=True)
        elif status == 'overdue':
            queryset = queryset.filter(is_returned=False, due_date__lt=date.today())
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_id_filter'] = self.request.GET.get('member_id', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['today'] = date.today()
        
        member_id = self.request.GET.get('member_id', '').strip()
        if member_id:
            member = Member.objects.filter(Q(member_id__iexact=member_id) | Q(name__icontains=member_id)).first()
            if member:
                context['selected_member'] = member
                records_qs = CirculationRecord.objects.filter(member=member)
                context['total_borrowed'] = records_qs.count()
                context['active_borrowed'] = records_qs.filter(is_returned=False).count()
                context['returned_count'] = records_qs.filter(is_returned=True).count()
                context['overdue_count'] = records_qs.filter(is_returned=False, due_date__lt=date.today()).count()
                context['total_fines'] = records_qs.aggregate(total=Sum('fine_amount'))['total'] or Decimal('0.00')
                
        return context

# Members List View
class MembersListView(StaffRequiredMixin, ListView):
    model = Member
    template_name = 'members.html'
    context_object_name = 'members'
    paginate_by = 15

    def get_queryset(self):
        queryset = Member.objects.annotate(
            active_loans=Count('circulation_records', filter=Q(circulation_records__is_returned=False))
        ).order_by('name')
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

# Register new member
class MemberCreateView(StaffRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'member_form.html'
    success_url = '/members/'

    def form_valid(self, form):
        messages.success(self.request, f"New member '{form.instance.name}' was successfully registered.")
        return super().form_valid(form)

# Custom Auth views
class CustomLoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                messages.success(request, f"Logged in successfully. Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
                form.add_error(None, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the form errors.")
            
        return render(request, self.template_name, {'form': form})

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('login')

    def post(self, request):
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('login')

# Portal marketing/landing views
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_books'] = Book.objects.select_related('author').order_by('-available_copies')[:4]
        return context

class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

# Custom 404 Handler
def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)
