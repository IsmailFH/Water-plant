from django.http import HttpResponse
from django.shortcuts import redirect

def manager_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('my_attendance')
    return wrapper_func

def worker_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')
    return wrapper_func
