from django import template
from django.utils import timezone
from datetime import datetime
import pytz

register = template.Library()

@register.filter
def endswith(value, arg):
    return str(value).lower().endswith(arg.lower())


@register.filter
def is_image(value):
    return str(value).lower().endswith(('.jpg', '.jpeg', '.png'))

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces"""
    if isinstance(value, str):
        return value.replace('_', ' ')
    return value


@register.filter
def format_ist_datetime(value):
    """
    Format datetime to IST (Asia/Kolkata) timezone.
    Converts to IST and displays as: "23 Apr 2026 02:30 PM"
    """
    if not value:
        return ''
    
    # Ensure value is timezone-aware
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        
        # Convert to IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        value_ist = value.astimezone(ist_tz)
        
        return value_ist.strftime('%d %b %Y %I:%M %p')
    
    return str(value)


@register.filter
def format_ist_date(value):
    """
    Format date to IST timezone (date only).
    Displays as: "23 Apr 2026"
    """
    if not value:
        return ''
    
    # Ensure value is timezone-aware
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        
        # Convert to IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        value_ist = value.astimezone(ist_tz)
        
        return value_ist.strftime('%d %b %Y')
    
    return str(value)


@register.filter
def format_ist_time(value):
    """
    Format time to IST timezone (time only).
    Displays as: "02:30 PM"
    """
    if not value:
        return ''
    
    # Ensure value is timezone-aware
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        
        # Convert to IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        value_ist = value.astimezone(ist_tz)
        
        return value_ist.strftime('%I:%M %p')
    
    return str(value)