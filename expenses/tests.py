from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from expenses.models import Expense

class ExpensesTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        
        self.expense1 = Expense.objects.create(
            user=self.user1,
            name='Groceries',
            category='Food',
            amount=50.00,
            date=date.today()
        )
        self.expense2 = Expense.objects.create(
            user=self.user2,
            name='Taxi',
            category='Travel',
            amount=15.00,
            date=date.today()
        )

    def test_expense_ownership(self):
        """Users should only see their own expenses."""
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Groceries')
        self.assertNotContains(response, 'Taxi')

    def test_budget_alert(self):
        """Adding an expense that exceeds the profile budget limit should add a warning alert."""
        # Set limit for user1
        self.user1.profile.monthly_budget_limit = 40.00
        self.user1.profile.save()

        self.client.login(username='user1', password='pass1')
        # user1 already has 50.00 expense, which is above 40.00
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['budget_alert'])
        self.assertEqual(response.context['budget_percentage'], 125)
