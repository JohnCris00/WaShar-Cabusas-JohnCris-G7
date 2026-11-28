import re
from datetime import date, datetime, timedelta

from django import forms

from .models import Reservation

SLOT_MINUTES = 30


def build_slots(shop):
    today = date.today()
    current = datetime.combine(today, shop.opening_time)
    closing = datetime.combine(today, shop.closing_time)
    slots = []
    while current < closing:
        slots.append(current.time())
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


class ReservationForm(forms.ModelForm):
    start_time = forms.ChoiceField(label="Time slot")

    class Meta:
        model = Reservation
        fields = ["service", "date", "start_time", "vehicle_plate", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, shop, customer, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.customer = customer
        self.fields["service"].queryset = shop.services.filter(is_active=True)
        self.fields["start_time"].choices = [
            (t.strftime("%H:%M"), t.strftime("%I:%M %p")) for t in build_slots(shop)
        ]
        self.fields["date"].widget.attrs["min"] = date.today().isoformat()
        if self.instance.pk:
            self.initial["start_time"] = self.instance.start_time.strftime("%H:%M")
        elif customer.vehicle_plate:
            self.initial.setdefault("vehicle_plate", customer.vehicle_plate)

    def clean_start_time(self):
        return datetime.strptime(self.cleaned_data["start_time"], "%H:%M").time()

    def clean_vehicle_plate(self):
        plate = self.cleaned_data["vehicle_plate"].strip().upper()
        if not re.match(r"^[A-Z0-9\- ]{3,15}$", plate):
            raise forms.ValidationError("Enter a valid plate number (letters, numbers, dash).")
        return plate

    def clean(self):
        cleaned = super().clean()
        service = cleaned.get("service")
        day = cleaned.get("date")
        start = cleaned.get("start_time")
        if not (service and day and start):
            return cleaned

        now = datetime.now()
        if day < now.date():
            self.add_error("date", "You can't book a date in the past.")
            return cleaned
        if day == now.date() and start <= now.time():
            self.add_error("start_time", "That time has already passed today.")
            return cleaned

        start_dt = datetime.combine(day, start)
        end_dt = start_dt + timedelta(minutes=service.duration_minutes)
        if end_dt > datetime.combine(day, self.shop.closing_time):
            self.add_error("start_time",
                           "This service would end after the shop closes. Choose an earlier slot.")
            return cleaned

        others = (Reservation.objects.filter(date=day)
                  .exclude(status=Reservation.Status.CANCELLED)
                  .select_related("service"))
        if self.instance.pk:
            others = others.exclude(pk=self.instance.pk)

        shop_count = 0
        for r in others:
            r_start = datetime.combine(day, r.start_time)
            r_end = r_start + timedelta(minutes=r.service.duration_minutes)
            if r_start < end_dt and start_dt < r_end:
                if r.customer_id == self.customer.pk:
                    self.add_error("start_time",
                                   "You already have a reservation that overlaps this time.")
                    return cleaned
                if r.shop_id == self.shop.pk:
                    shop_count += 1
        if shop_count >= self.shop.slot_capacity:
            self.add_error("start_time", "That time slot is fully booked. Please choose another.")
        return cleaned