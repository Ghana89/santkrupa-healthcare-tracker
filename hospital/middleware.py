# hospital/middleware.py
"""
Tenant middleware for multi-tenant context management.
Extracts clinic from URL and sets in thread-local storage.
"""

import threading
from django.contrib.auth.models import AnonymousUser

_thread_locals = threading.local()


def get_current_clinic():
    """Get current clinic from thread-local storage"""
    return getattr(_thread_locals, 'clinic', None)


def set_current_clinic(clinic):
    """Set current clinic in thread-local storage"""
    _thread_locals.clinic = clinic


def get_current_user():
    """Get current user from thread-local storage"""
    return getattr(_thread_locals, 'user', AnonymousUser())


def set_current_user(user):
    """Set current user in thread-local storage"""
    _thread_locals.user = user


class TenantMiddleware:
    """
    Middleware to extract and set clinic context.
    
    Clinic is extracted from:
    1. URL parameter (clinic_slug)
    2. User's clinic association (if authenticated)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract clinic from URL
        clinic_slug = None
        if request.resolver_match:
            clinic_slug = request.resolver_match.kwargs.get('clinic_slug')
        
        # Try to get clinic from URL
        if clinic_slug:
            try:
                from hospital.models import Clinic
                clinic = Clinic.objects.get(slug=clinic_slug)
                set_current_clinic(clinic)
                request.clinic = clinic
            except Exception as e:
                set_current_clinic(None)
                request.clinic = None
        
        # If user is authenticated, use their clinic
        elif request.user.is_authenticated:
            if hasattr(request.user, 'clinic'):
                set_current_clinic(request.user.clinic)
                request.clinic = request.user.clinic
            else:
                set_current_clinic(None)
                request.clinic = None
        else:
            set_current_clinic(None)
            request.clinic = None
        
        # Store user in thread-local
        set_current_user(request.user)
        
        try:
            response = self.get_response(request)
        finally:
            # Clean up thread-local storage
            set_current_clinic(None)
            set_current_user(AnonymousUser())
        
        return response
