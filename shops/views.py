from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ServiceForm, ShopForm
from .models import Service, Shop
from .permissions import customer_required, operator_required


# ---------- Operator: manage own shops ----------
@operator_required
def my_shops(request):
    shops = Shop.objects.filter(operator=request.user)
    return render(request, "shops/my_shops.html", {"shops": shops})


@operator_required
def shop_create(request):
    form = ShopForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        shop = form.save(commit=False)
        shop.operator = request.user
        shop.save()
        messages.success(request, f"Shop '{shop.name}' was created.")
        return redirect("shops:shop_detail", pk=shop.pk)
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "shops/shop_form.html", {"form": form, "title": "Add shop"})


@operator_required
def shop_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk, operator=request.user)
    return render(request, "shops/shop_detail.html",
                  {"shop": shop, "services": shop.services.all()})


@operator_required
def shop_update(request, pk):
    shop = get_object_or_404(Shop, pk=pk, operator=request.user)
    form = ShopForm(request.POST or None, instance=shop)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Shop updated.")
        return redirect("shops:shop_detail", pk=shop.pk)
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "shops/shop_form.html", {"form": form, "title": "Edit shop"})


@operator_required
def shop_delete(request, pk):
    shop = get_object_or_404(Shop, pk=pk, operator=request.user)
    if request.method == "POST":
        name = shop.name
        shop.delete()
        messages.success(request, f"Shop '{name}' was deleted.")
        return redirect("shops:my_shops")
    return render(request, "shops/confirm_delete.html", {"object": shop})


# ---------- Operator: services ----------
@operator_required
def service_create(request, shop_pk):
    shop = get_object_or_404(Shop, pk=shop_pk, operator=request.user)
    form = ServiceForm(request.POST or None, shop=shop)
    if request.method == "POST" and form.is_valid():
        service = form.save(commit=False)
        service.shop = shop
        service.save()
        messages.success(request, f"Service '{service.name}' was added.")
        return redirect("shops:shop_detail", pk=shop.pk)
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "shops/service_form.html",
                  {"form": form, "shop": shop, "title": "Add service"})


@operator_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk, shop__operator=request.user)
    form = ServiceForm(request.POST or None, instance=service, shop=service.shop)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Service updated.")
        return redirect("shops:shop_detail", pk=service.shop.pk)
    if request.method == "POST":
        messages.error(request, "Please fix the errors below.")
    return render(request, "shops/service_form.html",
                  {"form": form, "shop": service.shop, "title": "Edit service"})


@operator_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, shop__operator=request.user)
    shop_pk = service.shop.pk
    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted.")
        return redirect("shops:shop_detail", pk=shop_pk)
    return render(request, "shops/confirm_delete.html", {"object": service})


# ---------- Customer: Shop Finder ----------
@customer_required
def shop_finder(request):
    shops = Shop.objects.filter(is_active=True)
    q = request.GET.get("q", "").strip()
    if q:
        shops = shops.filter(
            Q(name__icontains=q) | Q(address__icontains=q) | Q(services__name__icontains=q)
        ).distinct()
    return render(request, "shops/shop_finder.html", {"shops": shops, "q": q})


@customer_required
def shop_public_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk, is_active=True)
    return render(request, "shops/shop_public_detail.html",
                  {"shop": shop, "services": shop.services.filter(is_active=True)})