from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegistrationForm


def home(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()  # password is hashed by UserCreationForm
            login(request, user)
            messages.success(request, f"Welcome to WaShar, {user.first_name}! Your account is ready.")
            return redirect("accounts:dashboard")
        messages.error(request, "We couldn't create your account. Fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


class WaSharLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Incorrect username or password.")
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name or user.username}.")
        return super().form_valid(form)


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    if request.user.is_operator:
        return redirect("accounts:operator_dashboard")
    return redirect("accounts:customer_dashboard")


@role_required("customer")
def customer_dashboard(request):
    return render(request, "accounts/dashboard_customer.html")


@role_required("operator")
def operator_dashboard(request):
    return render(request, "accounts/dashboard_operator.html")


@login_required
def profile(request):
    # Always the logged-in user's own record; no user id in the URL.
    return render(request, "accounts/profile.html", {"profile_user": request.user})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        messages.error(request, "Your profile wasn't saved. Fix the errors below.")
    return render(request, "accounts/profile_edit.html", {"form": form})


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)
