from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from investments.models import SIPInvestment, StockInvestment

class InvestmentsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='investor', password='pass')

    def test_sip_calculations(self):
        """SIP investments should correctly calculate profit/loss values and percentages."""
        sip = SIPInvestment.objects.create(
            user=self.user,
            fund_name='Index Fund',
            monthly_amount=100.00,
            start_date=date.today(),
            invested_amount=500.00,
            current_value=600.00
        )
        self.assertEqual(sip.profit_loss, 100.00)
        self.assertEqual(sip.profit_loss_pct, 20.0)

    def test_stock_calculations(self):
        """Stocks should correctly calculate total invested cost, current valuation, and performance."""
        stock = StockInvestment.objects.create(
            user=self.user,
            stock_name='Tesla',
            symbol='TSLA',
            quantity=10,
            buy_price=200.00,
            current_price=250.00
        )
        self.assertEqual(stock.invested_value, 2000.00)
        self.assertEqual(stock.current_value, 2500.00)
        self.assertEqual(stock.profit_loss, 500.00)
        self.assertEqual(stock.profit_loss_pct, 25.0)
