from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Shop(models.Model):
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shops"
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    slot_capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        if self.opening_time and self.closing_time and self.opening_time >= self.closing_time:
            raise ValidationError("Closing time must be later than opening time.")

    def __str__(self):
        return self.name


class Service(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("shop", "name")

    def clean(self):
        if self.price is not None and self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def __str__(self):
        return f"{self.name} ({self.shop.name})"