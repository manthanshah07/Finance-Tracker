from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'amount', 'date')
    list_filter = ('category', 'date', 'user')
    search_fields = ('name', 'category', 'user__username')
    ordering = ('-date',)
    date_hierarchy = 'date'
