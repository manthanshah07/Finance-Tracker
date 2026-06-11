import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime

from .models import SIPInvestment, StockInvestment
from .forms import SIPForm, StockForm

@login_required
def investment_dashboard(request):
    user = request.user
    
    # SIP calculations
    sips = SIPInvestment.objects.filter(user=user)
    total_sip_invested = sips.aggregate(Sum('invested_amount'))['invested_amount__sum'] or 0
    total_sip_current = sips.aggregate(Sum('current_value'))['current_value__sum'] or 0
    sip_pl = total_sip_current - total_sip_invested
    sip_pl_pct = (sip_pl / total_sip_invested * 100) if total_sip_invested > 0 else 0

    # Stock calculations
    stocks = StockInvestment.objects.filter(user=user)
    total_stock_invested = sum(s.invested_value for s in stocks)
    total_stock_current = sum(s.current_value for s in stocks)
    stock_pl = total_stock_current - total_stock_invested
    stock_pl_pct = (stock_pl / total_stock_invested * 100) if total_stock_invested > 0 else 0

    # Combined investments
    total_invested = total_sip_invested + total_stock_invested
    total_current = total_sip_current + total_stock_current
    total_pl = total_current - total_invested
    total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0

    context = {
        'sips': sips,
        'stocks': stocks,
        'total_sip_invested': total_sip_invested,
        'total_sip_current': total_sip_current,
        'sip_pl': sip_pl,
        'sip_pl_pct': sip_pl_pct,
        'total_stock_invested': total_stock_invested,
        'total_stock_current': total_stock_current,
        'stock_pl': stock_pl,
        'stock_pl_pct': stock_pl_pct,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_pl': total_pl,
        'total_pl_pct': total_pl_pct,
        'currency_symbol': get_currency_symbol(user.profile.currency)
    }
    return render(request, 'investments/investment_dashboard.html', context)

# --- SIP CRUD ---

@login_required
def sip_add(request):
    if request.method == 'POST':
        form = SIPForm(request.POST)
        if form.is_valid():
            sip = form.save(commit=False)
            sip.user = request.user
            sip.save()
            messages.success(request, "SIP Investment added successfully!")
            return redirect('investment_dashboard')
    else:
        form = SIPForm()
    return render(request, 'investments/sip_form.html', {'form': form, 'action': 'Add'})

@login_required
def sip_edit(request, pk):
    sip = get_object_or_404(SIPInvestment, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SIPForm(request.POST, instance=sip)
        if form.is_valid():
            form.save()
            messages.success(request, "SIP Investment updated successfully!")
            return redirect('investment_dashboard')
    else:
        form = SIPForm(instance=sip)
    return render(request, 'investments/sip_form.html', {'form': form, 'action': 'Edit'})

@login_required
def sip_delete(request, pk):
    sip = get_object_or_404(SIPInvestment, pk=pk, user=request.user)
    if request.method == 'POST':
        sip.delete()
        messages.success(request, "SIP Investment deleted successfully!")
        return redirect('investment_dashboard')
    return render(request, 'investments/sip_confirm_delete.html', {'sip': sip})

# --- Stock CRUD ---

@login_required
def stock_add(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            messages.success(request, "Stock position added successfully!")
            return redirect('investment_dashboard')
    else:
        form = StockForm()
    return render(request, 'investments/stock_form.html', {'form': form, 'action': 'Add'})

@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(StockInvestment, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock position updated successfully!")
            return redirect('investment_dashboard')
    else:
        form = StockForm(instance=stock)
    return render(request, 'investments/stock_form.html', {'form': form, 'action': 'Edit'})

@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(StockInvestment, pk=pk, user=request.user)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, "Stock position deleted successfully!")
        return redirect('investment_dashboard')
    return render(request, 'investments/stock_confirm_delete.html', {'stock': stock})

# --- CSV Import & Export ---

@login_required
def export_sips_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sips_{datetime.today().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Fund Name', 'Monthly Amount', 'Start Date', 'Invested Amount', 'Current Value'])

    sips = SIPInvestment.objects.filter(user=request.user)
    for s in sips:
        writer.writerow([s.fund_name, s.monthly_amount, s.start_date, s.invested_amount, s.current_value])

    return response

@login_required
def import_sips_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('investment_dashboard')

        try:
            file_data = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.reader(file_data)
            
            header = next(reader)
            header_clean = [h.strip().lower() for h in header]
            
            required = ['fund name', 'monthly amount', 'start date', 'invested amount', 'current value']
            if not all(col in header_clean for col in required):
                messages.error(request, "Invalid CSV headers. Must contain: Fund Name, Monthly Amount, Start Date, Invested Amount, Current Value")
                return redirect('investment_dashboard')

            col_map = {col: header_clean.index(col) for col in header_clean}
            
            success_count = 0
            for row in reader:
                if not row:
                    continue
                try:
                    fund_name = row[col_map['fund name']].strip()
                    monthly_amount = float(row[col_map['monthly amount']].strip())
                    start_date_str = row[col_map['start date']].strip()
                    invested_amount = float(row[col_map['invested amount']].strip())
                    current_value = float(row[col_map['current value']].strip())

                    # Parse Date
                    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                        try:
                            start_date = datetime.strptime(start_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        start_date = datetime.today().date()

                    SIPInvestment.objects.create(
                        user=request.user,
                        fund_name=fund_name,
                        monthly_amount=monthly_amount,
                        start_date=start_date,
                        invested_amount=invested_amount,
                        current_value=current_value
                    )
                    success_count += 1
                except Exception:
                    continue

            messages.success(request, f"Successfully imported {success_count} SIP investments!")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

    return redirect('investment_dashboard')


@login_required
def export_stocks_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="stocks_{datetime.today().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Stock Name', 'Symbol', 'Quantity', 'Buy Price', 'Current Price'])

    stocks = StockInvestment.objects.filter(user=request.user)
    for s in stocks:
        writer.writerow([s.stock_name, s.symbol, s.quantity, s.buy_price, s.current_price])

    return response

@login_required
def import_stocks_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('investment_dashboard')

        try:
            file_data = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.reader(file_data)
            
            header = next(reader)
            header_clean = [h.strip().lower() for h in header]
            
            required = ['stock name', 'symbol', 'quantity', 'buy price', 'current price']
            if not all(col in header_clean for col in required):
                messages.error(request, "Invalid CSV headers. Must contain: Stock Name, Symbol, Quantity, Buy Price, Current Price")
                return redirect('investment_dashboard')

            col_map = {col: header_clean.index(col) for col in header_clean}
            
            success_count = 0
            for row in reader:
                if not row:
                    continue
                try:
                    stock_name = row[col_map['stock name']].strip()
                    symbol = row[col_map['symbol']].strip().upper()
                    quantity = int(row[col_map['quantity']].strip())
                    buy_price = float(row[col_map['buy price']].strip())
                    current_price = float(row[col_map['current price']].strip())

                    StockInvestment.objects.create(
                        user=request.user,
                        stock_name=stock_name,
                        symbol=symbol,
                        quantity=quantity,
                        buy_price=buy_price,
                        current_price=current_price
                    )
                    success_count += 1
                except Exception:
                    continue

            messages.success(request, f"Successfully imported {success_count} stock holdings!")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

    return redirect('investment_dashboard')


# --- Helper ---

def get_currency_symbol(code):
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$'
    }
    return symbols.get(code, '$')
