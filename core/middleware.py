from django.conf import settings
from django.shortcuts import render

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is active in settings
        is_maintenance = getattr(settings, "MAINTENANCE_MODE", False)
        
        if is_maintenance:
            # Let staff/superusers bypass maintenance mode
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                return self.get_response(request)
            
            # Allow admin, store-admin, static, media, and social auth bypasses
            path = request.path
            if (
                path.startswith("/admin/") or 
                path.startswith("/store-admin/") or 
                path.startswith("/static/") or 
                path.startswith("/media/") or
                path.startswith("/auth/")
            ):
                return self.get_response(request)
                
            # Otherwise, render the premium maintenance page
            return render(request, "maintenance.html", status=503)

        return self.get_response(request)
