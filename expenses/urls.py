from django.urls import path
from .views import (
    expense_list, expense_add, expense_edit, expense_delete,
    export_expenses_csv, import_expenses_csv, generate_pdf_report
)

urlpatterns = [
    path('', expense_list, name='expense_list'),
    path('add/', expense_add, name='expense_add'),
    path('edit/<int:pk>/', expense_edit, name='expense_edit'),
    path('delete/<int:pk>/', expense_delete, name='expense_delete'),
    path('export/csv/', export_expenses_csv, name='export_expenses_csv'),
    path('import/csv/', import_expenses_csv, name='import_expenses_csv'),
    path('export/pdf/', generate_pdf_report, name='generate_pdf_report'),
]
