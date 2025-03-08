from django.shortcuts import redirect

EXEMPT_URLS = "/auth-signin/"  # Allow these pages without authentication

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in EXEMPT_URLS and "admin_username" not in request.session:
            return redirect("/auth-signin/")  # Redirect only if accessing a protected page
        return self.get_response(request)
