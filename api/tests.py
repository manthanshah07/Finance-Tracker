from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import date
from expenses.models import Expense

class ApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='apipassword123')
        self.other_user = User.objects.create_user(username='otheruser', password='apipassword123')
        
        # Create an expense for the main test user
        self.expense = Expense.objects.create(
            user=self.user,
            name='Coffee',
            category='Food',
            amount=5.50,
            date=date.today()
        )
        # Create an expense for the other user
        self.other_expense = Expense.objects.create(
            user=self.other_user,
            name='Flight',
            category='Travel',
            amount=350.00,
            date=date.today()
        )

    def test_unauthenticated_access_denied(self):
        """API endpoints must return 403 Forbidden for unauthenticated requests."""
        url = reverse('api_expense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_access_returns_user_data(self):
        """API endpoints must return 200 OK and show only the authenticated user's records."""
        self.client.login(username='apiuser', password='apipassword123')
        url = reverse('api_expense-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify length is 1 (only apiuser's expense)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Coffee')
        self.assertEqual(float(response.data[0]['amount']), 5.50)

    def test_authenticated_post_assigns_user(self):
        """Creating an item via POST should automatically associate it with the authenticated user."""
        self.client.login(username='apiuser', password='apipassword123')
        url = reverse('api_expense-list')
        data = {
            'name': 'Internet Bill',
            'category': 'Bills',
            'amount': '45.00',
            'date': str(date.today()),
            'notes': 'Monthly payment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify database check
        created_expense = Expense.objects.get(name='Internet Bill')
        self.assertEqual(created_expense.user, self.user)
        self.assertEqual(created_expense.amount, 45.00)
