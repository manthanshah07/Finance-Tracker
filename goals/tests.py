from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from goals.models import SavingsGoal

class GoalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='saver', password='pass')

    def test_savings_goal_progress_clamping(self):
        """Savings progress calculations must reflect accuracy and clamp at 100% when exceeded."""
        goal1 = SavingsGoal.objects.create(
            user=self.user,
            name='Emergency Fund',
            target_amount=1000.00,
            current_savings=250.00,
            target_date=date.today()
        )
        self.assertEqual(goal1.progress_pct, 25)

        # Over-savings
        goal2 = SavingsGoal.objects.create(
            user=self.user,
            name='Laptop',
            target_amount=500.00,
            current_savings=600.00,
            target_date=date.today()
        )
        self.assertEqual(goal2.progress_pct, 100)
