# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Author, Book, Member, CirculationRecord

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'biography_excerpt')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20

    def biography_excerpt(self, obj):
        return obj.biography[:75] + '...' if len(obj.biography) > 75 else obj.biography
    biography_excerpt.short_description = 'Biography'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies')
    list_filter = ('genre', 'author')
    search_fields = ('title', 'isbn', 'author__name')
    ordering = ('title',)
    list_per_page = 20

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_id', 'email', 'phone', 'joined_date')
    search_fields = ('name', 'member_id', 'email')
    list_filter = ('joined_date',)
    ordering = ('-joined_date',)
    list_per_page = 20

@admin.register(CirculationRecord)
class CirculationRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'due_date', 'return_date', 'fine_amount', 'is_returned')
    list_filter = ('is_returned', 'issue_date', 'due_date')
    search_fields = ('book__title', 'member__name', 'member__member_id')
    ordering = ('-issue_date',)
    list_per_page = 20
