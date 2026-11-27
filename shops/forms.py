from django import forms
from django.core.validators import RegexValidator

from .models import Service, Shop


class TimeInput(forms.TimeInput):
    input_type = "time"


class ShopForm(forms.ModelForm):
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        validators=[RegexValidator(r"^[0-9+\-\s()]{7,20}$", "Enter a valid contact number.")],
    )

    class Meta:
        model = Shop
        fields = ["name", "address", "contact_number", "opening_time",
                  "closing_time", "slot_capacity", "is_active"]
        widgets = {
            "opening_time": TimeInput(format="%H:%M"),
            "closing_time": TimeInput(format="%H:%M"),
        }

    def clean_slot_capacity(self):
        value = self.cleaned_data["slot_capacity"]
        if value < 1:
            raise forms.ValidationError("Capacity must be at least 1.")
        return value

    def clean(self):
        cleaned = super().clean()
        opening, closing = cleaned.get("opening_time"), cleaned.get("closing_time")
        if opening and closing and opening >= closing:
            self.add_error("closing_time", "Closing time must be later than opening time.")
        return cleaned


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "price", "duration_minutes", "is_active"]

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_duration_minutes(self):
        value = self.cleaned_data["duration_minutes"]
        if value < 5 or value > 480:
            raise forms.ValidationError("Duration must be between 5 and 480 minutes.")
        return value

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicate = Service.objects.filter(shop=self.shop, name__iexact=name)
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("This shop already has a service with that name.")
        return name