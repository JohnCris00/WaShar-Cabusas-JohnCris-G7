from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Vehicle owner"
        OPERATOR = "operator", "Shop operator"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^[0-9+\-\s()]{7,20}$", "Enter a valid contact number.")],
    )
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    # Vehicle details (used by customers only; blank for operators)
    vehicle_plate = models.CharField(max_length=15, blank=True)
    vehicle_model = models.CharField(max_length=60, blank=True)
    vehicle_type = models.CharField(
        max_length=15,
        blank=True,
        choices=[("sedan", "Sedan"), ("suv", "SUV"), ("van", "Van"), ("pickup", "Pickup"), ("motorcycle", "Motorcycle")],
    )

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    def __str__(self):
        return self.username
