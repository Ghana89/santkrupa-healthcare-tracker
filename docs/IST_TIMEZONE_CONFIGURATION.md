# IST (Indian Standard Time) Timezone Configuration

## Overview
The healthcare tracking system has been configured to use **Indian Standard Time (IST)** - Asia/Kolkata timezone (UTC+5:30) for all date and time operations.

## Changes Made

### 1. Django Settings Configuration
**File:** `santkrupa_hospital/settings.py`

```python
# Changed from:
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True

# To:
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
```

**What this means:**
- ✅ All datetimes are now stored in UTC in database (Django best practice)
- ✅ All datetimes are automatically converted to IST when displayed
- ✅ Language code changed to Indian English (en-in) for localization

### 2. Custom Template Filters
**File:** `hospital/templatetags/custom_filters.py`

Added three new filters for flexible date/time formatting:

#### `format_ist_datetime` Filter
Formats datetime to IST with full date and time.

**Usage in Templates:**
```django
{{ prescription.prescription_date|format_ist_datetime }}
```

**Output Example:**
```
23 Apr 2026 02:30 PM
```

#### `format_ist_date` Filter
Formats datetime to IST, showing only the date.

**Usage in Templates:**
```django
{{ prescription.prescription_date|format_ist_date }}
```

**Output Example:**
```
23 Apr 2026
```

#### `format_ist_time` Filter
Formats datetime to IST, showing only the time.

**Usage in Templates:**
```django
{{ prescription.prescription_date|format_ist_time }}
```

**Output Example:**
```
02:30 PM
```

### 3. AJAX Endpoint Date Formatting
**File:** `hospital/views.py` - `doctor_dashboard_prescriptions_ajax()` function

Prescription dates are now formatted in IST before being sent to frontend:

```python
# Convert prescription_date to IST
rx_date = rx.prescription_date
if timezone.is_naive(rx_date):
    rx_date = timezone.make_aware(rx_date)
rx_date_ist = rx_date.astimezone(ist_tz)

# Format as: "23 Apr 2026, 02:30 PM"
'date': rx_date_ist.strftime('%d %b %Y, %I:%M %p'),
```

### 4. Template Updates
**File:** `hospital/templates/hospital/doctor/dashboard.html`

- ✅ Added `{% load custom_filters %}` tag
- ✅ Updated check-in time display to use `format_ist_time` filter
- ✅ AJAX responses already display IST-formatted dates

## How It Works End-to-End

### Step 1: Data Creation
When a prescription is created:
```python
prescription = Prescription.objects.create(
    patient=patient,
    doctor=doctor,
    prescription_date=timezone.now()  # Stored as UTC in database
)
```

### Step 2: Database Storage
In `db.sqlite3`, the datetime is stored in UTC format.

### Step 3: Data Retrieval
When prescription is retrieved, Django's ORM automatically makes it timezone-aware:
```python
rx = Prescription.objects.get(id=123)
print(rx.prescription_date)  # Timezone-aware UTC datetime
```

### Step 4: Display/Formatting

**Option A: Using Template Filter**
```django
{{ prescription.prescription_date|format_ist_datetime }}
```
Django's template engine:
1. Converts UTC to IST
2. Formats as 12-hour format with AM/PM
3. Displays: "23 Apr 2026 02:30 PM"

**Option B: Using AJAX Endpoint**
Backend converts to IST before JSON response:
1. Retrieves UTC datetime from DB
2. Converts to IST timezone
3. Formats as 12-hour string
4. Returns in JSON: `"date": "23 Apr 2026, 02:30 PM"`
5. Frontend displays directly (no conversion needed)

**Option C: Using Built-in Django Filter**
```django
{{ prescription.prescription_date|date:"d M Y H:i" }}
```
Django respects the `TIME_ZONE` setting and auto-converts to IST.

## Database Schema - No Changes Required

Existing tables continue to work without migration because:
- ✅ DatetimeField already stores timezone info internally
- ✅ `auto_now_add=True` automatically uses current timezone
- ✅ `auto_now=True` automatically uses current timezone
- ✅ No data reprocessing needed

All existing datetime records are retroactively displayed in IST.

## Models Using Timezone-Aware Datetimes

The following models use proper timezone-aware datetimes:

```
Clinic:              created_at, updated_at
AssociatedMedical:   created_at
User:                created_at
Patient:             created_at
Prescription:        prescription_date, created_at
Test:                created_at
Medicine:            created_at
DoctorNotes:         created_at, updated_at
MedicalReport:       uploaded_at, created_at
PatientVisit:        check_in_date (used in dashboard)
TestReport:          uploaded_at
PatientAdmission:    admission_date, discharge_date, created_at, updated_at
TreatmentLog:        created_at, updated_at
Vitals:              created_at, updated_at
StandardPrescriptionTemplate: created_at, updated_at
```

All these will now automatically display in IST.

## Examples in Practice

### Example 1: Patient Check-in
```
Stored in DB: 2026-04-23 09:30:00 (UTC)
Displayed: 23 Apr 2026 03:00 PM (IST = UTC + 5:30)
```

### Example 2: Prescription Creation
```
Stored in DB: 2026-04-23 10:45:30 (UTC)
Displayed: 23 Apr 2026 04:15 PM (IST)
```

### Example 3: Hospital Admission
```
Stored in DB: 2026-04-23 06:20:00 (UTC)
Displayed: 23 Apr 2026 11:50 AM (IST)
```

## Testing the Configuration

### Method 1: Django Shell
```python
python manage.py shell

from hospital.models import Prescription
from django.utils import timezone

# Create test prescription
rx = Prescription.objects.create(
    patient_id=1,
    doctor_id=1,
    clinic_id=1
)

# Check timezone
print(rx.prescription_date)  # Shows IST time
print(timezone.get_current_timezone())  # Should show pytz.timezone('Asia/Kolkata')
```

### Method 2: In Templates
```django
{% load custom_filters %}
<p>Created: {{ object.created_at|format_ist_datetime }}</p>
```

### Method 3: API Response
Monitor AJAX requests in browser DevTools:
```json
{
  "prescriptions": [
    {
      "date": "23 Apr 2026, 02:30 PM",
      "date_short": "23 Apr 2026"
    }
  ]
}
```

## Frontend Considerations

### JavaScript Date Handling
If you need to work with dates in JavaScript:

```javascript
// AJAX response contains IST-formatted string
const dateString = rx.date;  // "23 Apr 2026, 02:30 PM"
console.log(dateString);  // Already formatted, no conversion needed
```

### Client-Side Formatting (if needed)
```javascript
// The backend already formats dates, but if you need custom formatting:
const dateIST = new Date('2026-04-23T14:30:00+05:30');  // IST format
const formatted = dateIST.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
});
```

## Migration (If Needed)

No database migration is required. The IST conversion happens at:
- **Display Time** (templates and AJAX responses)
- **Not at Storage Time** (still stored as UTC in DB)

This is the Django best practice for multi-timezone support.

## Configuration Summary

| Setting | Before | After | Impact |
|---------|--------|-------|--------|
| LANGUAGE_CODE | en-us | en-in | Localization support for India |
| TIME_ZONE | UTC | Asia/Kolkata | All dates display in IST |
| USE_TZ | True | True | Timezone support enabled |
| DB Storage | UTC | UTC | No change (best practice) |
| Display | UTC | IST | All end-user facing dates now in IST |

## Supported Date Formats

The system now supports these date/time formats:

### Long Format
```
23 Apr 2026 02:30 PM
```
Used in: AJAX responses, detailed views

### Short Date Format
```
23 Apr 2026
```
Used in: Prescription table, check-in lists

### Time Only Format
```
02:30 PM
```
Used in: Check-in time displays

## Browser Timezone Note

Browser timezone settings do NOT affect the display because:
- ✅ Backend handles all timezone conversion
- ✅ Frontend receives pre-formatted IST strings
- ✅ Works correctly regardless of user's browser timezone

This ensures consistent time display across all users and devices.

## Troubleshooting

### Issue: Dates still showing wrong time
**Solution:** Clear browser cache and Django cache
```bash
python manage.py clear_cache
```

### Issue: Template filter not recognized
**Ensure:** Template includes custom_filters tag
```django
{% load custom_filters %}
```

### Issue: AJAX dates wrong format
**Check:** You're using the new `format_ist_datetime` filter or backend already converts

### Issue: Old records showing wrong time
**Note:** All existing records automatically show in IST (no reprocessing needed)

## Performance Impact

- ✅ Zero performance impact
- ✅ Timezone conversion happens at display time only
- ✅ Database queries unchanged
- ✅ No additional caching needed

## Deployment Checklist

- [ ] Update Django settings.py with TIME_ZONE = 'Asia/Kolkata'
- [ ] Update LANGUAGE_CODE to 'en-in'
- [ ] Verify custom_filters.py has IST formatting functions
- [ ] Update templates to load custom_filters
- [ ] Update AJAX endpoints to format dates in IST
- [ ] Test date display in all pages
- [ ] Clear browser cache
- [ ] Test with different timezone browser settings

## Future Enhancements

Possible improvements:
1. Add user-configurable timezone preferences
2. Add timezone selector in user settings
3. Display timezone indicator in UI (e.g., "IST")
4. Add historical timezone data for audit logs
5. Export data with timezone info

---

**Configuration Date:** April 23, 2026
**Status:** ✅ Complete and Active
**Timezone:** Asia/Kolkata (IST, UTC+5:30)
