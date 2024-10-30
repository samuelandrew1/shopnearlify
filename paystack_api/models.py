import secrets
from django.db import models

from django.conf import settings


from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone


class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=""
    )
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_created",)

    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(10)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount) * 100

    @staticmethod
    def total_payments(period="daily"):
        """Returns the sum of payments for the specified period"""
        today = timezone.now()
        if period == "daily":
            start_date = today - timedelta(days=1)
        elif period == "weekly":
            start_date = today - timedelta(weeks=1)
        elif period == "monthly":
            start_date = today - timedelta(days=30)
        elif period == "annual":
            start_date = today - timedelta(days=365)
        else:
            start_date = today

        payments = Payment.objects.filter(date_created__gte=start_date).aggregate(
            total=Sum("amount")
        )
        return payments["total"] or 0
