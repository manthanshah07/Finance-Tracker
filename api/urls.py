from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseViewSet,
    SIPInvestmentViewSet,
    StockInvestmentViewSet,
    SavingsGoalViewSet
)

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='api_expense')
router.register(r'sips', SIPInvestmentViewSet, basename='api_sip')
router.register(r'stocks', StockInvestmentViewSet, basename='api_stock')
router.register(r'goals', SavingsGoalViewSet, basename='api_goal')

urlpatterns = [
    path('', include(router.urls)),
]
