from datetime import datetime, timedelta

from django.conf import settings
from django.db import models

from shops.models import Service, Shop


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="reservations")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="reservations")
    date = models.DateField()
    start_time = models.TimeField()
    vehicle_plate = models.CharField(max_length=15)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    @property
    def end_time(self):
        start = datetime.combine(self.date, self.start_time)
        return (start + timedelta(minutes=self.service.duration_minutes)).time()

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    def __str__(self):
        return f"{self.shop.name} - {self.service.name} on {self.date} {self.start_time:%H:%M}"