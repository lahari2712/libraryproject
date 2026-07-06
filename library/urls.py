from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('catalog/', views.BookCatalogView.as_view(), name='catalog'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('issue/', views.BookIssueView.as_view(), name='book_issue'),
    path('return/<int:pk>/', views.BookReturnView.as_view(), name='book_return'),
    path('members/', views.MembersListView.as_view(), name='members'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('history/', views.MemberHistoryView.as_view(), name='history'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]
