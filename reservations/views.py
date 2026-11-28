from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shops.models import Shop
from shops.permissions import customer_required, operator_required

from .forms import ReservationForm
from .models import Reservation

TRANSITIONS = {
    "confirm": (Reservation.Status.PENDING, Reservation.Status.CONFIRMED, "confirmed"),
    "reject": (Reservation.Status.PENDING, Reservation.Status.CANCELLED, "rejected"),
    "complete": (Reservation.Status.CONFIRMED, Reservation.Status.COMPLETED, "marked as completed"),
    "cancel": (Reservation.Status.CONFIRMED, Reservation.Status.CANCELLED, "cancelled"),
}


# ---------- Customer ----------
@customer_required
def reservation_create(request, shop_pk):
    shop = get_object_or_404(Shop, pk=shop_pk, is_active=True)
    form = ReservationForm(request.POST or None, shop=shop, customer=request.user)
    if request.method == "POST" and form.is_valid():
        reservation = form.save(commit=False)
        reservation.customer = request.user
        reservation.shop = shop
        reservation.save()
        messages.success(request, "Reservation submitted. Waiting for the shop to confirm.")
        return redirect("reservations:my_reservations")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "reservations/reservation_form.html",
                  {"form": form, "shop": shop, "title": "Reserve a slot"})


@customer_required
def my_reservations(request):
    reservations = (Reservation.objects.filter(customer=request.user)
                    .select_related("shop", "service"))
    status = request.GET.get("status", "")
    if status in Reservation.Status.values:
        reservations = reservations.filter(status=status)
    return render(request, "reservations/my_reservations.html",
                  {"reservations": reservations, "status": status,
                   "statuses": Reservation.Status.choices})


@customer_required
def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    if not reservation.is_pending:
        messages.error(request, "Only pending reservations can be edited.")
        return redirect("reservations:my_reservations")
    form = ReservationForm(request.POST or None, instance=reservation,
                           shop=reservation.shop, customer=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Reservation updated.")
        return redirect("reservations:my_reservations")
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "reservations/reservation_form.html",
                  {"form": form, "shop": reservation.shop, "title": "Edit reservation"})


@customer_required
@require_POST
def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    if reservation.is_pending:
        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        messages.success(request, "Reservation cancelled.")
    else:
        messages.error(request, "Only pending reservations can be cancelled.")
    return redirect("reservations:my_reservations")


@customer_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user,
                                    status=Reservation.Status.CANCELLED)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Reservation record deleted.")
        return redirect("reservations:my_reservations")
    return render(request, "shops/confirm_delete.html", {"object": reservation})


# ---------- Operator ----------
@operator_required
def shop_reservations(request):
    reservations = (Reservation.objects.filter(shop__operator=request.user)
                    .select_related("shop", "service", "customer"))
    status = request.GET.get("status", "")
    if status in Reservation.Status.values:
        reservations = reservations.filter(status=status)
    return render(request, "reservations/shop_reservations.html",
                  {"reservations": reservations, "status": status,
                   "statuses": Reservation.Status.choices})


@operator_required
@require_POST
def reservation_set_status(request, pk, action):
    reservation = get_object_or_404(Reservation, pk=pk, shop__operator=request.user)
    if action not in TRANSITIONS:
        messages.error(request, "Unknown action.")
        return redirect("reservations:shop_reservations")
    required, new_status, label = TRANSITIONS[action]
    if reservation.status != required:
        messages.error(request, f"This reservation is {reservation.get_status_display().lower()} "
                                f"and can't be {label}.")
    else:
        reservation.status = new_status
        reservation.save()
        messages.success(request, f"Reservation {label}.")
    return redirect("reservations:shop_reservations")