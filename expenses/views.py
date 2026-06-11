import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.db.models import Sum, Q
from datetime import datetime

from .models import Expense
from .forms import ExpenseForm

# PDF Generation imports
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    
    # Filtering and Searching
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search_query:
        expenses = expenses.filter(name__icontains=search_query)
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    # Calculate filtered total
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'expenses': expenses,
        'categories': Expense.CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': category_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_amount': total_amount,
        'currency_symbol': get_currency_symbol(request.user.profile.currency)
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            
            # Check monthly budget alert
            check_budget_alert(request)
            
            messages.success(request, "Expense added successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Add'})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            check_budget_alert(request)
            messages.success(request, "Expense updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Edit'})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

# --- CSV Import & Export ---

@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="expenses_{datetime.today().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Expense Name', 'Category', 'Amount', 'Date', 'Notes'])

    expenses = Expense.objects.filter(user=request.user)
    for e in expenses:
        writer.writerow([e.name, e.category, e.amount, e.date, e.notes or ''])

    return response

@login_required
def import_expenses_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('expense_list')

        try:
            file_data = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.reader(file_data)
            
            # Read header
            header = next(reader)
            # Basic header validation
            expected_headers = ['expense name', 'category', 'amount', 'date', 'notes']
            header_clean = [h.strip().lower() for h in header]
            
            # Ensure required fields are there
            if not all(col in header_clean for col in ['expense name', 'category', 'amount', 'date']):
                messages.error(request, "Invalid CSV headers. Must contain: Expense Name, Category, Amount, Date")
                return redirect('expense_list')

            # Map header positions
            col_map = {col: header_clean.index(col) for col in header_clean}
            
            success_count = 0
            for row in reader:
                if not row:
                    continue
                try:
                    name = row[col_map['expense name']].strip()
                    category = row[col_map['category']].strip()
                    amount_str = row[col_map['amount']].strip()
                    date_str = row[col_map['date']].strip()
                    notes = row[col_map['notes']].strip() if 'notes' in col_map else ''

                    # Validate category choices
                    valid_categories = [c[0] for c in Expense.CATEGORY_CHOICES]
                    if category not in valid_categories:
                        category = 'Other' # Default to other if invalid

                    # Parse values
                    amount = float(amount_str)
                    
                    # Parse date formats: YYYY-MM-DD or MM/DD/YYYY
                    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                        try:
                            date_val = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        # If date parsing fails, skip or use today
                        date_val = datetime.today().date()

                    Expense.objects.create(
                        user=request.user,
                        name=name,
                        category=category,
                        amount=amount,
                        date=date_val,
                        notes=notes
                    )
                    success_count += 1
                except Exception:
                    # Skip rows with conversion issues
                    continue

            messages.success(request, f"Successfully imported {success_count} expenses!")
            check_budget_alert(request)
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
    return redirect('expense_list')

# --- PDF Report Generation ---

@login_required
def generate_pdf_report(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#718096"),
        spaceAfter=25
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#2D3748")
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white
    )

    # Add Title & Subtitle
    story.append(Paragraph("Personal Finance Statement", title_style))
    today_str = datetime.today().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {today_str} | Generated for: {request.user.username.capitalize()}", subtitle_style))
    story.append(Spacer(1, 10))

    # Summary Section
    story.append(Paragraph("Monthly Summary", section_style))
    expenses = Expense.objects.filter(user=request.user)
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    curr_month = datetime.today().month
    curr_year = datetime.today().year
    month_spent = expenses.filter(date__year=curr_year, date__month=curr_month).aggregate(Sum('amount'))['amount__sum'] or 0
    budget_limit = request.user.profile.monthly_budget_limit
    currency = get_currency_symbol(request.user.profile.currency)

    summary_data = [
        [Paragraph("Metric", header_style), Paragraph("Value", header_style)],
        [Paragraph("Total Lifetime Spending", body_style), Paragraph(f"{currency} {total_spent:,.2f}", body_style)],
        [Paragraph("Current Month Spending", body_style), Paragraph(f"{currency} {month_spent:,.2f}", body_style)],
        [Paragraph("Monthly Budget Limit", body_style), Paragraph(f"{currency} {budget_limit:,.2f}" if budget_limit > 0 else "Not Set", body_style)],
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#2B6CB0")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Detailed Expenses Table
    story.append(Paragraph("Detailed Expenses List", section_style))
    all_expenses = expenses.order_by('-date')[:50]  # Limit to recent 50 for report sizing
    
    expense_headers = [
        Paragraph("Name", header_style),
        Paragraph("Category", header_style),
        Paragraph("Amount", header_style),
        Paragraph("Date", header_style),
        Paragraph("Notes", header_style)
    ]
    expense_data = [expense_headers]
    
    for e in all_expenses:
        expense_data.append([
            Paragraph(e.name, body_style),
            Paragraph(e.category, body_style),
            Paragraph(f"{currency} {e.amount:,.2f}", body_style),
            Paragraph(e.date.strftime("%Y-%m-%d"), body_style),
            Paragraph(e.notes or "-", body_style)
        ])

    expense_table = Table(expense_data, colWidths=[130, 90, 80, 80, 160])
    expense_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(expense_table)

    # Build Document
    doc.build(story)
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f"finance_report_{datetime.today().strftime('%Y%m%d')}.pdf")

# --- Helper Functions ---

def get_currency_symbol(code):
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$'
    }
    return symbols.get(code, '$')

def check_budget_alert(request):
    user = request.user
    profile = user.profile
    budget_limit = profile.monthly_budget_limit
    
    if budget_limit > 0:
        today = datetime.today()
        month_spent = Expense.objects.filter(
            user=user, 
            date__year=today.year, 
            date__month=today.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if month_spent > budget_limit:
            messages.warning(
                request, 
                f"BUDGET ALERT: You have exceeded your monthly budget of {get_currency_symbol(profile.currency)} {budget_limit}! Total spent: {get_currency_symbol(profile.currency)} {month_spent}."
            )
