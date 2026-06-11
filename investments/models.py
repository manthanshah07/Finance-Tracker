from django.db import models
from django.contrib.auth.models import User

class SIPInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sips')
    fund_name = models.CharField(max_length=150)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    invested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def profit_loss(self):
        return self.current_value - self.invested_amount

    @property
    def profit_loss_pct(self):
        if self.invested_amount > 0:
            return (self.profit_loss / self.invested_amount) * 100
        return 0

    class Meta:
        ordering = ['fund_name']

    def __str__(self):
        return f"{self.fund_name} - SIP"


class StockInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stocks')
    stock_name = models.CharField(max_length=150)
    symbol = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def invested_value(self):
        return self.quantity * self.buy_price

    @property
    def current_value(self):
        return self.quantity * self.current_price

    @property
    def profit_loss(self):
        return self.current_value - self.invested_value

    @property
    def profit_loss_pct(self):
        if self.buy_price > 0:
            return ((self.current_price - self.buy_price) / self.buy_price) * 100
        return 0

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return f"{self.stock_name} ({self.symbol})"
