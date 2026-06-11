from django.urls import path
from .views import (
    investment_dashboard,
    sip_add, sip_edit, sip_delete, export_sips_csv, import_sips_csv,
    stock_add, stock_edit, stock_delete, export_stocks_csv, import_stocks_csv
)

urlpatterns = [
    path('', investment_dashboard, name='investment_dashboard'),
    
    # SIPs
    path('sip/add/', sip_add, name='sip_add'),
    path('sip/edit/<int:pk>/', sip_edit, name='sip_edit'),
    path('sip/delete/<int:pk>/', sip_delete, name='sip_delete'),
    path('sip/export/csv/', export_sips_csv, name='export_sips_csv'),
    path('sip/import/csv/', import_sips_csv, name='import_sips_csv'),
    
    # Stocks
    path('stock/add/', stock_add, name='stock_add'),
    path('stock/edit/<int:pk>/', stock_edit, name='stock_edit'),
    path('stock/delete/<int:pk>/', stock_delete, name='stock_delete'),
    path('stock/export/csv/', export_stocks_csv, name='export_stocks_csv'),
    path('stock/import/csv/', import_stocks_csv, name='import_stocks_csv'),
]
