from rest_framework import viewsets, permissions
from expenses.models import Expense
from investments.models import SIPInvestment, StockInvestment
from goals.models import SavingsGoal

from .serializers import (
    ExpenseSerializer,
    SIPInvestmentSerializer,
    StockInvestmentSerializer,
    SavingsGoalSerializer
)

class UserDataMixin:
    """
    Mixin to automatically filter querysets by the logged-in user
    and assign the logged-in user during object creation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(UserDataMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class SIPInvestmentViewSet(UserDataMixin, viewsets.ModelViewSet):
    queryset = SIPInvestment.objects.all()
    serializer_class = SIPInvestmentSerializer


class StockInvestmentViewSet(UserDataMixin, viewsets.ModelViewSet):
    queryset = StockInvestment.objects.all()
    serializer_class = StockInvestmentSerializer


class SavingsGoalViewSet(UserDataMixin, viewsets.ModelViewSet):
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer
