from django import forms
from .models import SIPInvestment, StockInvestment

class SIPForm(forms.ModelForm):
    class Meta:
        model = SIPInvestment
        fields = ['fund_name', 'monthly_amount', 'start_date', 'invested_amount', 'current_value']
        widgets = {
            'fund_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Vanguard 500 Index Fund'}),
            'monthly_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'invested_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = StockInvestment
        fields = ['stock_name', 'symbol', 'quantity', 'buy_price', 'current_price']
        widgets = {
            'stock_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Apple Inc.'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AAPL'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'buy_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
