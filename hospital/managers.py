# hospital/managers.py
"""
Custom managers for multi-tenant queries.
Auto-filter all queries by current clinic.
"""

import threading
from django.db import models
from django.core.exceptions import ImproperlyConfigured

_thread_locals = threading.local()


def get_current_clinic():
    """Get current clinic from thread-local storage"""
    return getattr(_thread_locals, 'clinic', None)


def set_current_clinic(clinic):
    """Set current clinic in thread-local storage"""
    _thread_locals.clinic = clinic


class ClinicQuerySet(models.QuerySet):
    """QuerySet that filters by current clinic"""
    
    def for_clinic(self, clinic):
        """Filter queryset for specific clinic"""
        if not clinic:
            raise ImproperlyConfigured("Clinic context is required")
        return self.filter(clinic=clinic)


class ClinicManager(models.Manager):
    """Manager that auto-filters by current clinic"""
    
    def get_queryset(self):
        """Override to automatically filter by clinic"""
        qs = super().get_queryset()
        clinic = get_current_clinic()
        
        # If no clinic context, return empty queryset (safe default)
        if clinic:
            return qs.filter(clinic=clinic)
        return qs.none()
    
    def for_clinic(self, clinic):
        """Get queryset for specific clinic"""
        return self.get_queryset().filter(clinic=clinic)
    
    def all_clinics(self):
        """Get all records (bypass clinic filtering)"""
        return super().get_queryset()
