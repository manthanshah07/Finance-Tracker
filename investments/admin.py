from django.contrib import admin
from .models import SIPInvestment, StockInvestment

@admin.register(SIPInvestment)
class SIPInvestmentAdmin(admin.ModelAdmin):
    list_display = ('fund_name', 'user', 'monthly_amount', 'start_date', 'invested_amount', 'current_value')
    list_filter = ('start_date', 'user')
    search_fields = ('fund_name', 'user__username')
    ordering = ('fund_name',)


@admin.register(StockInvestment)
class StockInvestmentAdmin(admin.ModelAdmin):
    list_display = ('stock_name', 'symbol', 'user', 'quantity', 'buy_price', 'current_price')
    list_filter = ('symbol', 'user')
    search_fields = ('stock_name', 'symbol', 'user__username')
    ordering = ('symbol',)
