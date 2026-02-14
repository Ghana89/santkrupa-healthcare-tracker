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
    """Manager for multi-tenant queries"""
    
    def get_queryset(self):
        """Return base queryset without auto-filtering"""
        return super().get_queryset()
    
    def for_clinic(self, clinic):
        """Get queryset for specific clinic"""
        if not clinic:
            raise ImproperlyConfigured("Clinic context is required")
        return self.get_queryset().filter(clinic=clinic)
    
    def all_clinics(self):
        """Get all records (explicitly show intent)"""
        return self.get_queryset()
