from rest_framework import serializers
from expenses.models import Expense
from investments.models import SIPInvestment, StockInvestment
from goals.models import SavingsGoal

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'name', 'category', 'amount', 'date', 'notes']
        read_only_fields = ['id']


class SIPInvestmentSerializer(serializers.ModelSerializer):
    profit_loss = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_loss_pct = serializers.FloatField(read_only=True)

    class Meta:
        model = SIPInvestment
        fields = ['id', 'fund_name', 'monthly_amount', 'start_date', 'invested_amount', 'current_value', 'profit_loss', 'profit_loss_pct']
        read_only_fields = ['id']


class StockInvestmentSerializer(serializers.ModelSerializer):
    invested_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    current_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_loss = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_loss_pct = serializers.FloatField(read_only=True)

    class Meta:
        model = StockInvestment
        fields = ['id', 'stock_name', 'symbol', 'quantity', 'buy_price', 'current_price', 'invested_value', 'current_value', 'profit_loss', 'profit_loss_pct']
        read_only_fields = ['id']


class SavingsGoalSerializer(serializers.ModelSerializer):
    progress_pct = serializers.IntegerField(read_only=True)

    class Meta:
        model = SavingsGoal
        fields = ['id', 'name', 'target_amount', 'current_savings', 'target_date', 'progress_pct']
        read_only_fields = ['id']
