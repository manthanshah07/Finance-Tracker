from django.db import models
from django.contrib.auth.models import User

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    target_date = models.DateField()

    @property
    def progress_pct(self):
        if self.target_amount > 0:
            pct = int((self.current_savings / self.target_amount) * 100)
            return min(pct, 100)
        return 0

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f"{self.name} - {self.progress_pct}%"
