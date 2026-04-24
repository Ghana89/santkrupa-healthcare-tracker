# IST Timezone Implementation - Code Examples

## Real-World Examples

### Example 1: Doctor Dashboard Prescription List

**In Template:**
```django
{% load custom_filters %}

<table>
    <tr>
        <td>John Doe</td>
        <td>{{ prescription.prescription_date|format_ist_date }}</td>
        <td>Pending</td>
    </tr>
</table>
```

**Output:**
```
| John Doe | 23 Apr 2026 | Pending |
```

---

### Example 2: Check-in Time Display

**Before (OLD - UTC):**
```django
{{ visit.check_in_date|date:"H:i" }}
Output: 09:30  (This was actually UTC, not IST!)
```

**After (NEW - IST):**
```django
{% load custom_filters %}
{{ visit.check_in_date|format_ist_time }}
Output: 03:00 PM  (Correct IST time)
```

---

### Example 3: AJAX Response Processing

**Backend (Python):**
```python
def doctor_dashboard_prescriptions_ajax(request, clinic_slug=None):
    from django.utils import timezone
    ist_tz = timezone.pytz.timezone('Asia/Kolkata')
    
    prescriptions_data = []
    for rx in prescriptions:
        # Convert to IST
        rx_date = rx.prescription_date
        if timezone.is_naive(rx_date):
            rx_date = timezone.make_aware(rx_date)
        rx_date_ist = rx_date.astimezone(ist_tz)
        
        prescriptions_data.append({
            'id': rx.id,
            'patient_name': rx.patient.patient_name,
            'date': rx_date_ist.strftime('%d %b %Y, %I:%M %p'),  # IST formatted
            'status': rx.get_status_display(),
        })
    
    return JsonResponse({'prescriptions': prescriptions_data})
```

**Frontend (JavaScript):**
```javascript
fetch('/clinic/santkrupa/doctor/dashboard/prescriptions-ajax/')
    .then(response => response.json())
    .then(data => {
        data.prescriptions.forEach(rx => {
            // rx.date is already IST formatted as "23 Apr 2026, 02:30 PM"
            console.log(rx.date);  // No conversion needed!
        });
    });
```

**HTML Output:**
```
Date: 23 Apr 2026, 02:30 PM
```

---

### Example 4: Creating New Records with IST

**In Django View:**
```python
from django.utils import timezone
from hospital.models import PatientVisit

# Using timezone.now() automatically uses IST now
visit = PatientVisit.objects.create(
    patient=patient,
    clinic=clinic,
    check_in_date=timezone.now()  # Automatically IST aware
)

# Verify in IST
from django.utils import timezone
ist_tz = timezone.pytz.timezone('Asia/Kolkata')
print(visit.check_in_date.astimezone(ist_tz))
# Output: 2026-04-23 14:30:00+05:30 (IST)
```

---

### Example 5: Querying by Date in IST

**Find all prescriptions created today (IST):**
```python
from django.utils import timezone
from datetime import timedelta
from hospital.models import Prescription

ist_tz = timezone.pytz.timezone('Asia/Kolkata')
now_ist = timezone.now().astimezone(ist_tz)
today_start = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
today_end = today_start + timedelta(days=1)

prescriptions_today = Prescription.objects.filter(
    prescription_date__range=[today_start, today_end]
)
```

---

### Example 6: Audit Log Entry with IST

**Model:**
```python
class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        ist_tz = timezone.pytz.timezone('Asia/Kolkata')
        ts_ist = self.timestamp.astimezone(ist_tz)
        return f"{self.action} - {ts_ist.strftime('%d %b %Y %I:%M %p IST')}"
```

**Template:**
```django
{% load custom_filters %}

<div>
    <p>{{ log.action }}</p>
    <p>{{ log.performed_by }}</p>
    <p>{{ log.timestamp|format_ist_datetime }} IST</p>
</div>
```

**Output:**
```
Prescription Created
Dr. Rajesh Kumbhar
23 Apr 2026 02:30 PM IST
```

---

### Example 7: Date Range Filter

**In Admin or View:**
```python
from django.utils import timezone
from datetime import timedelta

# Last 7 days in IST
ist_tz = timezone.pytz.timezone('Asia/Kolkata')
end_date = timezone.now().astimezone(ist_tz)
start_date = end_date - timedelta(days=7)

recent_prescriptions = Prescription.objects.filter(
    prescription_date__gte=start_date,
    prescription_date__lte=end_date
)
```

---

### Example 8: Batch Update with Timestamp

**Update discharge date for admitted patients:**
```python
from django.utils import timezone
from hospital.models import PatientAdmission

# Get all active admissions
active = PatientAdmission.objects.filter(status='admitted')

# Update discharge date to now (IST)
for admission in active:
    if some_condition:
        admission.discharge_date = timezone.now()  # Now IST
        admission.save()
```

---

### Example 9: Report Generation

**Generate report with times:**
```python
from django.utils import timezone
from datetime import datetime

def generate_daily_report():
    ist_tz = timezone.pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist_tz)
    
    report = {
        'report_date': now.strftime('%d %b %Y'),
        'report_time': now.strftime('%I:%M %p IST'),
        'total_visits': visits_today.count(),
        'total_admissions': admissions_today.count(),
    }
    
    return report
```

**Output:**
```json
{
    "report_date": "23 Apr 2026",
    "report_time": "02:30 PM IST",
    "total_visits": 45,
    "total_admissions": 3
}
```

---

### Example 10: Combining Multiple Dates

**Timeline view in template:**
```django
{% load custom_filters %}

<div class="timeline">
    <h3>Patient Journey</h3>
    <p>Registered: {{ patient.created_at|format_ist_datetime }}</p>
    <p>First Visit: {{ first_visit.check_in_date|format_ist_datetime }}</p>
    <p>Last Prescription: {{ last_prescription.prescription_date|format_ist_datetime }}</p>
    <p>Admission Date: {{ admission.admission_date|format_ist_datetime }}</p>
    {% if admission.discharge_date %}
        <p>Discharged: {{ admission.discharge_date|format_ist_datetime }}</p>
    {% endif %}
</div>
```

**Output:**
```
Patient Journey
Registered: 15 Apr 2026 10:30 AM
First Visit: 17 Apr 2026 02:15 PM
Last Prescription: 23 Apr 2026 03:30 PM
Admission Date: 20 Apr 2026 09:00 AM
Discharged: 23 Apr 2026 11:45 AM
```

---

## Key Takeaways

1. **Always use `timezone.now()`** instead of `datetime.now()`
2. **Filters handle conversion** - No need for manual conversion in templates
3. **AJAX endpoints should format** - Backend formats before JSON response
4. **Database uses UTC** - Best practice for multi-timezone systems
5. **Display uses IST** - All user-facing content in IST

## Common Mistakes to Avoid

❌ **DON'T:**
```python
from datetime import datetime
now = datetime.now()  # Wrong - naive datetime in UTC
```

✅ **DO:**
```python
from django.utils import timezone
now = timezone.now()  # Correct - timezone-aware in IST
```

❌ **DON'T:**
```django
{{ date_field|date:"d M Y" }}
<!-- Without timezone setting, might show UTC -->
```

✅ **DO:**
```django
{% load custom_filters %}
{{ date_field|format_ist_date }}
<!-- Always shows IST -->
```

---

**Examples Date:** April 23, 2026
