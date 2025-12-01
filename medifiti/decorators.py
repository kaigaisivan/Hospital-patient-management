"""Role-based access control decorators for protecting views."""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    """Redirect to login if user is not authenticated as admin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    """Redirect to login if user is not authenticated as doctor."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'doctor':
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def patient_required(view_func):
    """Redirect to login if user is not authenticated as patient."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'patient':
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_redirect(view_func):
    """Redirect to login if user is not authenticated."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
