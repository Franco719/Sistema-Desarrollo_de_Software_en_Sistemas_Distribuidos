from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def role_required(role_name, redirect_to='home', message="No tenés permisos para acceder a esta página."):
    """Decorator: requiere que request.user esté en el Group `role_name`."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.groups.filter(name=role_name).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, message)
            return redirect(redirect_to)
        return _wrapped
    return decorator