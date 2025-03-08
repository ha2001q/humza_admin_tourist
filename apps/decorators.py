from django.shortcuts import redirect

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if "admin_username" not in request.session:
            if request.path not in ["/auth-signin/"]:  # Allow login page
                return redirect("/auth-signin/")
        return view_func(request, *args, **kwargs)
    return wrapper
