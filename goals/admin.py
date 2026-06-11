from django.contrib import admin
from .models import SavingsGoal

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_savings', 'target_date', 'progress_pct')
    list_filter = ('target_date', 'user')
    search_fields = ('name', 'user__username')
    ordering = ('target_date',)
