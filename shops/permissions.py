from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def operator_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_operator:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def customer_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_customer:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper