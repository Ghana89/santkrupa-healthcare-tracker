# Testing Guide - Dashboard AJAX Prescription Management

## Quick Test Using Browser Console

After implementing the fix and accessing the dashboard at `/clinic/santkrupa/doctor/dashboard/`, open browser DevTools and run:

```javascript
// Test 1: Verify URL construction
const clinicSlug = "{{ clinic.slug }}" || '';
console.log("Clinic Slug:", clinicSlug);
console.log("Expected URL:", clinicSlug ? `/clinic/${clinicSlug}/doctor/dashboard/prescriptions-ajax/?page=1` : "/doctor/dashboard/prescriptions-ajax/?page=1");

// Test 2: Manually trigger prescription load
loadPrescriptions(1);

// Test 3: Check for successful response
// In Network tab, look for the AJAX request and verify:
// - Status: 200
// - Response: Contains "success": true
// - Data: Contains prescriptions array
```

## Test Scenarios

### Scenario 1: Basic Load
1. Navigate to: `/clinic/santkrupa/doctor/dashboard/`
2. Wait for dashboard to render
3. **Expected:** Prescriptions table populates with data
4. **Check Network Tab:** Request to `/clinic/santkrupa/doctor/dashboard/prescriptions-ajax/` returns 200

### Scenario 2: Search by Patient Name
1. On dashboard, enter patient name in search box
2. Click "🔍 Search" button
3. **Expected:** Table shows only matching prescriptions
4. **Network:** Request includes `search=<patient_name>`

### Scenario 3: Search by Patient ID
1. On dashboard, enter patient ID (e.g., "P001") in search box
2. Click "🔍 Search" button
3. **Expected:** Table shows only matching prescriptions
4. **Network:** Request includes `search=P001`

### Scenario 4: Filter by Status
1. Select "Pending" from status dropdown
2. Click "🔍 Search" button
3. **Expected:** Shows only pending prescriptions
4. **Network:** Request includes `status=pending`

### Scenario 5: Pagination
1. If more than 10 prescriptions exist, "Next →" button appears
2. Click "Next →"
3. **Expected:** Shows next 10 items
4. **Page info updates:** "Page 2 of X"

### Scenario 6: Delete Prescription
1. Click "🗑 Delete" on any prescription
2. Confirm deletion
3. **Expected:** Prescription removed from table
4. **Table reloads:** Automatically shows updated list

### Scenario 7: Combined Search + Filter
1. Search for patient name AND select status
2. Click search
3. **Expected:** Shows matching results filtered by both criteria

## Debugging Commands

### Check URL Construction in Browser

```javascript
// In console, verify the URL that will be called
const params = new URLSearchParams({ page: 1, search: '', status: '' });
const clinicSlug = document.querySelector('[data-clinic-slug]')?.dataset.clinicSlug || '';
console.log(`Requesting: /clinic/${clinicSlug}/doctor/dashboard/prescriptions-ajax/?${params}`);
```

### Monitor AJAX Calls

In browser DevTools → Network tab:
1. Filter by: "prescriptions-ajax"
2. Perform any action (search, pagination, etc.)
3. Verify each request:
   - **URL:** Correct path included
   - **Status:** 200 OK
   - **Method:** GET
   - **Response:** Valid JSON

### Check Python Backend

```python
# In Django shell
from hospital.models import Prescription, Doctor, User

# Get test doctor
user = User.objects.get(username='doctor_username')
doctor = Doctor.objects.get(user=user)

# Check prescriptions count
print(f"Total prescriptions: {Prescription.objects.filter(doctor=doctor).count()}")
print(f"Pending prescriptions: {Prescription.objects.filter(doctor=doctor, status='pending').count()}")

# Verify endpoint is accessible
from django.test import Client
from django.contrib.auth import get_user_model

client = Client()
user = get_user_model().objects.get(username='doctor_username')
client.force_login(user)
response = client.get('/clinic/santkrupa/doctor/dashboard/prescriptions-ajax/?page=1')
print(f"Response status: {response.status_code}")
print(f"Response JSON: {response.json()}")
```

## Network Request Analysis

### Expected Request Format
```
GET /clinic/santkrupa/doctor/dashboard/prescriptions-ajax/?page=1&search=&status= HTTP/1.1
Host: localhost:8000
Cookie: csrftoken=...;
```

### Expected Response Format
```json
{
  "success": true,
  "prescriptions": [
    {
      "id": 123,
      "patient_name": "John Doe",
      "patient_id": "P001",
      "date": "Apr 23, 2026",
      "status": "Pending",
      "status_value": "pending",
      "tests_count": 3,
      "medicines_count": 5,
      "clinic_slug": "santkrupa"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

## Troubleshooting Checklist

- [ ] Dashboard accessible at `/clinic/santkrupa/doctor/dashboard/` (200)
- [ ] AJAX request URL includes clinic slug in path
- [ ] AJAX endpoint returns status 200
- [ ] Response contains valid JSON
- [ ] Response has "success": true
- [ ] Prescriptions array populated with data
- [ ] Pagination info shows correct counts
- [ ] Search input accepts text
- [ ] Status filter dropdown works
- [ ] Search button triggers AJAX call
- [ ] Pagination buttons navigate correctly
- [ ] Delete button confirms and removes item
- [ ] No console errors in browser DevTools
- [ ] No errors in Django server logs

## Performance Benchmarks

After fix, expect:
- **AJAX response time:** < 200ms (for <100 prescriptions)
- **Page load time:** Same as before (static content loads first)
- **Search latency:** < 100ms
- **Pagination load:** < 100ms

## Rollback Instructions

If needed, revert to original static table:

1. In `dashboard.html`, replace the prescriptions section with original version
2. Remove AJAX endpoint from `views.py`
3. Remove URL pattern from `urls.py`

See `DELIVERY_SUMMARY.md` for previous dashboard version.

---

**Last Updated:** April 23, 2026
