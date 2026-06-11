from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
import json

from .forms import UserRegisterForm, UserUpdateForm, UserProfileForm
from .models import UserProfile

# Import models from other apps (we will create them next)
from expenses.models import Expense
from investments.models import SIPInvestment, StockInvestment
from goals.models import SavingsGoal

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"Account created for {user.username}! You can now login.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, "Your password was successfully updated!")
        return super().form_valid(form)

@login_required
def dashboard_view(request):
    user = request.user
    profile = user.profile
    today = timezone.now()
    
    # --- 1. EXPENSES ---
    expenses_query = Expense.objects.filter(user=user)
    total_expenses = expenses_query.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Monthly Expenses (current month)
    curr_month_expenses = expenses_query.filter(
        date__year=today.year, 
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Budget alerts
    budget_limit = profile.monthly_budget_limit
    budget_alert = False
    budget_percentage = 0
    if budget_limit > 0:
        budget_percentage = int((curr_month_expenses / budget_limit) * 100)
        if curr_month_expenses > budget_limit:
            budget_alert = True

    # --- 2. INVESTMENTS (SIP) ---
    sips_query = SIPInvestment.objects.filter(user=user)
    total_sip_invested = sips_query.aggregate(Sum('invested_amount'))['invested_amount__sum'] or 0
    total_sip_current = sips_query.aggregate(Sum('current_value'))['current_value__sum'] or 0

    # --- 3. STOCKS ---
    stocks = StockInvestment.objects.filter(user=user)
    total_stock_invested = sum(s.quantity * s.buy_price for s in stocks)
    total_stock_current = sum(s.quantity * s.current_price for s in stocks)

    # Combined Investment Metrics
    total_invested = total_sip_invested + total_stock_invested
    total_current_value = total_sip_current + total_stock_current
    investment_profit_loss = total_current_value - total_invested
    
    investment_pl_pct = 0
    if total_invested > 0:
        investment_pl_pct = (investment_profit_loss / total_invested) * 100

    # --- 4. SAVINGS GOALS ---
    goals = SavingsGoal.objects.filter(user=user)
    total_goals_count = goals.count()
    completed_goals = 0
    total_target = 0
    total_saved = 0
    
    goals_data = []
    for g in goals:
        pct = int((g.current_savings / g.target_amount) * 100) if g.target_amount > 0 else 0
        pct = min(pct, 100)
        if pct >= 100:
            completed_goals += 1
        total_target += g.target_amount
        total_saved += g.current_savings
        goals_data.append({
            'goal': g,
            'pct': pct
        })
        
    avg_goal_progress = int((total_saved / total_target) * 100) if total_target > 0 else 0
    avg_goal_progress = min(avg_goal_progress, 100)

    # --- 5. CHARTS (CHART.JS DATA) ---
    # A. Expense by Category (Pie Chart)
    category_breakdown = expenses_query.values('category').annotate(total=Sum('amount'))
    categories = [item['category'] for item in category_breakdown]
    category_totals = [float(item['total']) for item in category_breakdown]
    
    # B. Monthly Expenses over last 6 months (Bar Chart)
    monthly_expenses_labels = []
    monthly_expenses_values = []
    for i in range(5, -1, -1):
        # Calculate month & year offset
        check_date = today - timedelta(days=i*30)
        month_name = check_date.strftime('%B %Y')
        monthly_expenses_labels.append(month_name)
        
        m_expenses = expenses_query.filter(
            date__year=check_date.year, 
            date__month=check_date.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expenses_values.append(float(m_expenses))

    # C. Wealth Growth Line Chart (SIP Growth trend helper)
    # We will simulate monthly cumulative investment value vs current value growth
    investment_growth_labels = []
    investment_growth_invested = []
    investment_growth_current = []
    
    # Calculate for the last 6 months
    for i in range(5, -1, -1):
        check_date = today - timedelta(days=i*30)
        investment_growth_labels.append(check_date.strftime('%b %Y'))
        
        # Accumulate SIPs starting on or before this month
        sip_total_i = 0
        sip_total_c = 0
        for s in sips_query:
            if s.start_date <= check_date.date():
                # Approximation based on months elapsed
                months_elapsed = (check_date.year - s.start_date.year) * 12 + (check_date.month - s.start_date.month) + 1
                months_elapsed = max(months_elapsed, 1)
                
                # Assume standard linear growth for historical display
                sip_total_i += s.monthly_amount * months_elapsed
                if s.invested_amount > 0:
                    growth_ratio = s.current_value / s.invested_amount
                    sip_total_c += (s.monthly_amount * months_elapsed) * growth_ratio
                else:
                    sip_total_c += s.monthly_amount * months_elapsed
                    
        # Accumulate stock holdings as static line for visual ease
        stock_total_i = total_stock_invested
        stock_total_c = total_stock_current
        
        investment_growth_invested.append(float(sip_total_i + stock_total_i))
        investment_growth_current.append(float(sip_total_c + stock_total_c))

    chart_data = {
        'categories': categories,
        'category_totals': category_totals,
        'monthly_labels': monthly_expenses_labels,
        'monthly_values': monthly_expenses_values,
        'growth_labels': investment_growth_labels,
        'growth_invested': investment_growth_invested,
        'growth_current': investment_growth_current,
    }

    # High-level financial summary
    net_worth = total_current_value + total_saved - total_expenses

    context = {
        'currency_symbol': get_currency_symbol(profile.currency),
        'total_expenses': total_expenses,
        'curr_month_expenses': curr_month_expenses,
        'budget_limit': budget_limit,
        'budget_alert': budget_alert,
        'budget_percentage': budget_percentage,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'investment_profit_loss': investment_profit_loss,
        'investment_pl_pct': investment_pl_pct,
        'net_worth': net_worth,
        'goals': goals_data,
        'completed_goals': completed_goals,
        'total_goals_count': total_goals_count,
        'avg_goal_progress': avg_goal_progress,
        'chart_data': json.dumps(chart_data)
    }

    return render(request, 'dashboard.html', context)


def get_currency_symbol(code):
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    return symbols.get(code, '$')
