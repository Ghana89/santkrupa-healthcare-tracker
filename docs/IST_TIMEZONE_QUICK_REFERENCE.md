# IST Timezone Configuration - Quick Reference

## Summary of Changes

### 1. Settings Updated ✅
```python
# File: santkrupa_hospital/settings.py
TIME_ZONE = 'Asia/Kolkata'  # Changed from 'UTC'
LANGUAGE_CODE = 'en-in'     # Changed from 'en-us'
USE_TZ = True               # Already set (kept as is)
```

### 2. New Template Filters Added ✅
```python
# File: hospital/templatetags/custom_filters.py
@register.filter
def format_ist_datetime(value):
    """Full date+time: "23 Apr 2026 02:30 PM" """
    # Auto-converts to IST

@register.filter
def format_ist_date(value):
    """Date only: "23 Apr 2026" """
    # Auto-converts to IST

@register.filter
def format_ist_time(value):
    """Time only: "02:30 PM" """
    # Auto-converts to IST
```

### 3. AJAX Endpoint Updated ✅
```python
# File: hospital/views.py
# doctor_dashboard_prescriptions_ajax() function
# NOW converts dates to IST before JSON response
'date': rx_date_ist.strftime('%d %b %Y, %I:%M %p'),
'date_short': rx_date_ist.strftime('%d %b %Y'),
```

### 4. Templates Updated ✅
```django
{# File: hospital/templates/hospital/doctor/dashboard.html #}
{% load custom_filters %}
{{ visit.check_in_date|format_ist_time }}
```

## How to Use

### In Django Templates
```django
{% load custom_filters %}

{# Full datetime with time #}
{{ prescription.prescription_date|format_ist_datetime }}
Output: 23 Apr 2026 02:30 PM

{# Date only #}
{{ prescription.prescription_date|format_ist_date }}
Output: 23 Apr 2026

{# Time only #}
{{ prescription.prescription_date|format_ist_time }}
Output: 02:30 PM
```

### In Django Shell
```python
from hospital.models import Prescription
from django.utils import timezone

rx = Prescription.objects.first()
print(rx.prescription_date)  # Already shows IST

# Get current time in IST
now = timezone.now()
print(now)  # Shows in IST
```

### In AJAX Responses
```javascript
// Backend already formats dates, frontend receives:
{
  "date": "23 Apr 2026, 02:30 PM",  // Already IST formatted
  "date_short": "23 Apr 2026"
}
```

## Date Format Reference

| Filter | Format | Example |
|--------|--------|---------|
| `format_ist_datetime` | `dd MMM YYYY hh:mm AM/PM` | 23 Apr 2026 02:30 PM |
| `format_ist_date` | `dd MMM YYYY` | 23 Apr 2026 |
| `format_ist_time` | `hh:mm AM/PM` | 02:30 PM |

## Important Points

✅ **Database Storage:** Still UTC (best practice)  
✅ **Display:** All converted to IST automatically  
✅ **No Migration Needed:** Only settings changed  
✅ **Backward Compatible:** Existing data works as-is  
✅ **Works Globally:** All users see IST regardless of location  

## Verification

### Check 1: Settings Applied
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.TIME_ZONE)  # Should show: Asia/Kolkata
>>> print(settings.LANGUAGE_CODE)  # Should show: en-in
```

### Check 2: Template Filters Available
```django
{% load custom_filters %}
<!-- If this works without error, filters are loaded correctly -->
```

### Check 3: Dates Showing Correct Time
1. Navigate to doctor dashboard
2. Check check-in times → should show IST
3. Check prescription dates in AJAX table → should show IST
4. Compare with actual clock → should match

## Usage in New Code

When adding new datetime displays:

### Option 1: Use Custom Filter (Recommended)
```django
{% load custom_filters %}
<p>{{ model.datetime_field|format_ist_datetime }}</p>
```

### Option 2: Django Built-in Filter
```django
{{ model.datetime_field|date:"d M Y g:i A" }}
<!-- Automatically respects TIME_ZONE setting -->
```

### Option 3: AJAX/API
```python
from django.utils import timezone
ist_tz = timezone.pytz.timezone('Asia/Kolkata')
datetime_ist = utc_datetime.astimezone(ist_tz)
formatted = datetime_ist.strftime('%d %b %Y, %I:%M %p')
```

## Timezone Offset Reference

IST = UTC + 5 hours 30 minutes

| UTC Time | IST Time |
|----------|----------|
| 00:00 | 05:30 |
| 06:00 | 11:30 |
| 09:30 | 15:00 (3:00 PM) |
| 12:00 | 17:30 (5:30 PM) |
| 18:00 | 23:30 (11:30 PM) |

## Troubleshooting Tips

### Dates still showing in UTC
- [ ] Clear browser cache (Ctrl+Shift+Del)
- [ ] Restart Django development server
- [ ] Check settings.py has correct TIME_ZONE

### Template filter not recognized
- [ ] Ensure `{% load custom_filters %}` in template
- [ ] Check custom_filters.py exists and is valid
- [ ] Restart Django server after editing filters

### AJAX dates wrong
- [ ] Check views.py has timezone conversion code
- [ ] Look at Network tab in DevTools for actual response
- [ ] Verify response is IST formatted before frontend receives

## Files Modified

1. ✅ `santkrupa_hospital/settings.py` - TimeZone config
2. ✅ `hospital/templatetags/custom_filters.py` - IST filters
3. ✅ `hospital/views.py` - AJAX date conversion
4. ✅ `hospital/templates/hospital/doctor/dashboard.html` - Template updates

## Testing Checklist

- [ ] Navigate to doctor dashboard
- [ ] Check visible times match IST
- [ ] Perform AJAX search
- [ ] Verify returned dates are IST formatted
- [ ] Check different browser timezones (not affected)
- [ ] Test on mobile (should work same)
- [ ] Verify old prescriptions show IST times
- [ ] Check all models with datetime fields

## Performance Impact

- ✅ **Zero** - Happens at display time only
- ✅ Database queries unchanged
- ✅ No additional server load
- ✅ No caching issues

## Next Steps

If needed, can add:
1. User-configurable timezone preferences
2. Timezone indicator in UI (e.g., "IST")
3. Multiple timezone support for multi-location clinics
4. Audit logs with timezone info

---

**Implementation Date:** April 23, 2026  
**Status:** ✅ Complete  
**Timezone:** Asia/Kolkata (IST, UTC+5:30)
