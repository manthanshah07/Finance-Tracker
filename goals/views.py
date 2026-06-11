from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import SavingsGoal
from .forms import GoalForm

@login_required
def goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    
    total_target = goals.aggregate(Sum('target_amount'))['target_amount__sum'] or 0
    total_saved = goals.aggregate(Sum('current_savings'))['current_savings__sum'] or 0
    
    overall_progress = 0
    if total_target > 0:
        overall_progress = int((total_saved / total_target) * 100)
        overall_progress = min(overall_progress, 100)
        
    goals_data = []
    for g in goals:
        goals_data.append({
            'goal': g,
            'pct': g.progress_pct
        })

    context = {
        'goals': goals_data,
        'total_target': total_target,
        'total_saved': total_saved,
        'overall_progress': overall_progress,
        'currency_symbol': get_currency_symbol(request.user.profile.currency)
    }
    return render(request, 'goals/goal_list.html', context)

@login_required
def goal_add(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings Goal added successfully!")
            return redirect('goal_list')
    else:
        form = GoalForm()
    return render(request, 'goals/goal_form.html', {'form': form, 'action': 'Add'})

@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Savings Goal updated successfully!")
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'goals/goal_form.html', {'form': form, 'action': 'Edit'})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Savings Goal deleted successfully!")
        return redirect('goal_list')
    return render(request, 'goals/goal_confirm_delete.html', {'goal': goal})

# --- Helper ---

def get_currency_symbol(code):
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$'
    }
    return symbols.get(code, '$')
