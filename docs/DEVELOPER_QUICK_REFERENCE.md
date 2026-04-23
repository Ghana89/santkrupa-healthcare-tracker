# Multi-Tenant Quick Reference Guide

## For Developers Working with Multi-Tenant System

### 1. Core Concepts (30 seconds)

```
Single Clinic (Before):
  └─ 1 Hospital
     ├─ 100 Patients
     ├─ 20 Doctors
     └─ 5 Receptionists

Multi-Tenant (After):
  ├─ Clinic 1 (Santkrupa)
  │  ├─ 100 Patients (isolated from Clinic 2)
  │  ├─ 20 Doctors
  │  └─ 5 Receptionists
  └─ Clinic 2 (Apollo)
     ├─ 150 Patients (isolated from Clinic 1)
     ├─ 30 Doctors
     └─ 8 Receptionists
```

### 2. Most Important: Always Know Current Clinic

```python
from hospital.managers import get_current_clinic

# ALWAYS available in views (middleware sets it)
clinic = get_current_clinic()
```

### 3. Querying Data (The Right Way)

#### ❌ WRONG - Gets all data from all clinics
```python
all_patients = Patient.objects.all()  # DON'T DO THIS!
```

#### ✅ RIGHT - Auto-filtered by current clinic
```python
from hospital.managers import get_current_clinic

clinic = get_current_clinic()
clinic_patients = Patient.objects.all()  # Already filtered!

# Verify filtering worked:
print(clinic_patients.query)  # Should have WHERE clinic_id = X
```

#### ✅ ALSO RIGHT - Explicit filtering (if needed)
```python
clinic = Clinic.objects.get(slug='santkrupa')
clinic_patients = Patient.objects.filter(clinic=clinic)
```

### 4. Creating Objects (Auto-Set Clinic)

#### ✅ Recommended: Let code handle clinic
```python
from hospital.managers import get_current_clinic

def create_patient_view(request):
    clinic = get_current_clinic()
    
    patient = Patient.objects.create(
        clinic=clinic,  # Set clinic explicitly
        patient_name='John Doe',
        phone_number='9876543210',
        # ... other fields
    )
    return patient
```

#### Alternative: Via Form
```python
def create_patient_form(request):
    form = PatientForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.clinic = get_current_clinic()  # Set before save
        instance.save()
```

### 5. URL Structure (Know Your Paths)

```
/clinic/<slug>/...        ← Clinic-specific routes
/clinic/santkrupa/patient/dashboard/

/login/                   ← Global routes
/logout/
/
```

### 6. Common Tasks (Copy-Paste Ready)

#### Get Current Clinic
```python
from hospital.managers import get_current_clinic
clinic = get_current_clinic()
print(f"Current clinic: {clinic.name}")
```

#### Get Clinic Users
```python
clinic = get_current_clinic()
users = clinic.users.all()  # reverse relation
doctors = clinic.doctors.all()  # reverse relation
patients = clinic.patients.all()  # reverse relation
```

#### Filter by Clinic Explicitly
```python
clinic = Clinic.objects.get(slug='santkrupa')
patients = Patient.objects.filter(clinic=clinic)
doctors = Doctor.objects.filter(clinic=clinic)
```

#### Create New Clinic
```python
from hospital.models import Clinic

clinic = Clinic.objects.create(
    name='New Hospital',
    slug='new-hospital',
    address='123 Main St',
    city='Mumbai',
    state='Maharashtra',
    zip_code='400001',
    phone_number='+91-22-XXXX-XXXX',
    email='admin@newhospital.com',
    registration_number='REG-2024-NEW',
    subscription_status='trial',
    max_doctors=20,
    max_patients=500,
    max_receptionists=5,
)
print(f"Created: {clinic}")
```

#### Create User in Clinic
```python
from hospital.models import User, Clinic

clinic = Clinic.objects.get(slug='santkrupa')
user = User.objects.create_user(
    username='dr_smith',
    password='secure123',
    email='smith@santkrupa.com',
    clinic=clinic,
    role='doctor'
)
```

#### Create Patient in Clinic
```python
from hospital.models import Patient, Clinic

clinic = Clinic.objects.get(slug='santkrupa')
patient = Patient.objects.create(
    clinic=clinic,
    patient_name='John Doe',
    age=45,
    phone_number='9876543210',
    email='john@example.com',
    address='123 Patient St',
    city='Bangalore'
)
print(f"Patient ID: {patient.patient_id}")  # PT-1-2024-001
```

#### Query Within Current Clinic
```python
from hospital.managers import get_current_clinic

clinic = get_current_clinic()
# All auto-filtered by clinic
doctors = Doctor.objects.all()
prescriptions = Prescription.objects.all()
tests = Test.objects.all()
```

#### Admin-Only: Query Across All Clinics
```python
from hospital.managers import ClinicManager

# Bypass clinic filtering
all_patients = Patient.objects.all_clinics()
all_doctors = Doctor.objects.all_clinics()
```

### 7. View Template (Common Pattern)

```python
from django.shortcuts import render
from hospital.managers import get_current_clinic
from hospital.models import Patient

def patient_list(request):
    clinic = get_current_clinic()
    
    # This is auto-filtered by clinic
    patients = Patient.objects.all()
    
    context = {
        'clinic': clinic,
        'patients': patients,
        'clinic_name': clinic.name,  # For page title
    }
    return render(request, 'patient_list.html', context)
```

### 8. Testing Multi-Tenancy

```python
# test_models.py
from django.test import TestCase
from hospital.models import Clinic, Patient
from hospital.managers import get_current_clinic, set_current_clinic

class MultiTenantTestCase(TestCase):
    def setUp(self):
        # Create two clinics
        self.clinic1 = Clinic.objects.create(
            name='Clinic 1', slug='clinic-1',
            # ... required fields
        )
        self.clinic2 = Clinic.objects.create(
            name='Clinic 2', slug='clinic-2',
            # ... required fields
        )
        
        # Create patients in different clinics
        self.patient1 = Patient.objects.create(
            clinic=self.clinic1,
            patient_name='Patient 1',
            # ... required fields
        )
        self.patient2 = Patient.objects.create(
            clinic=self.clinic2,
            patient_name='Patient 2',
            # ... required fields
        )
    
    def test_isolation(self):
        # Set context to clinic1
        set_current_clinic(self.clinic1)
        
        # Query should only return patient1
        patients = Patient.objects.all()
        self.assertEqual(patients.count(), 1)
        self.assertEqual(patients[0].patient_name, 'Patient 1')
        
        # Set context to clinic2
        set_current_clinic(self.clinic2)
        
        # Query should only return patient2
        patients = Patient.objects.all()
        self.assertEqual(patients.count(), 1)
        self.assertEqual(patients[0].patient_name, 'Patient 2')
```

### 9. Common Mistakes (Don't Do These!)

#### ❌ Forget to Set Clinic on Create
```python
# WRONG - Will fail with foreign key constraint
patient = Patient.objects.create(
    patient_name='John',
    # clinic not set!
)
```

#### ❌ Use Hard-Coded Clinic IDs
```python
# WRONG - Will break if clinic_id changes
Patient.objects.filter(clinic_id=1)

# RIGHT
clinic = get_current_clinic()
Patient.objects.filter(clinic=clinic)
```

#### ❌ Query Without Context
```python
# WRONG - Will show data from ALL clinics
patients = Patient.objects.all()

# RIGHT
set_current_clinic(clinic)  # First set context
patients = Patient.objects.all()  # Then query
```

#### ❌ Redirect Without Clinic Slug
```python
# WRONG - URL is clinic-unaware
return redirect('patient_dashboard')

# RIGHT - Include clinic slug
return redirect('patient_dashboard', clinic_slug='santkrupa')
# In template:
# <a href="{% url 'patient_dashboard' clinic.slug %}">Dashboard</a>
```

### 10. File Locations (Where to Find What)

```
hospital/
├── managers.py          ← Multi-tenant query logic
├── middleware.py        ← Clinic context management
├── models.py            ← Clinic model + clinic_id fields
├── views.py             ← (Update in Phase 2)
├── forms.py             ← (Update in Phase 2)
├── admin.py             ← (Update in Phase 2)
└── migrations/          ← Database schema versions

santkrupa_hospital/
├── settings.py          ← TenantMiddleware registered
├── urls.py              ← Multi-tenant URL routing
└── wsgi.py
```

### 11. Debugging Checklist

**Query returning wrong data?**
1. Check: `get_current_clinic()` - is it the right clinic?
2. Check: Query SQL - does WHERE have `clinic_id = X`?
3. Check: Model has `objects = ClinicManager()`?

**Clinic context not set?**
1. Check: URL has clinic slug? `/clinic/<slug>/...`
2. Check: TenantMiddleware registered in settings.py?
3. Check: Middleware position after AuthenticationMiddleware?

**Foreign key constraint error?**
1. Check: Did you set `clinic=get_current_clinic()` on create?
2. Check: clinic_id column exists on model?

**Unique constraint violation?**
1. Check: Is same data in different clinics? (OK - unique per clinic)
2. Check: Multiple records in SAME clinic? (Problem - fix data)

### 12. Key Files Modified (What Changed)

| File | Change | Impact |
|------|--------|--------|
| hospital/managers.py | NEW | Auto-filter queries |
| hospital/middleware.py | NEW | Set clinic context |
| hospital/models.py | 9 models updated | Add clinic_id FK |
| settings.py | +1 line | Register middleware |
| urls.py | Restructured | Multi-tenant routing |

### 13. Before/After Comparison

```
BEFORE (Single-Tenant):
  Patient.objects.all()
  → Gets ALL patients from ALL time

AFTER (Multi-Tenant):
  Patient.objects.all()
  → Gets only current clinic's patients
  → Clinic set by middleware from URL
  → Safe default - no data leakage
```

### 14. Key Advantages

✅ **Data Isolation** - Clinics completely separate  
✅ **Automatic Filtering** - Prevents accidental data access  
✅ **Scalable** - Add new clinics without code changes  
✅ **Thread-Safe** - Context stored in thread-local  
✅ **URL-Driven** - Clinic determined from URL slug  

### 15. When to Ask for Help

- Query returning data from multiple clinics?
- Need to bypass clinic filtering (admin task)?
- Creating new model - unsure about clinic_id?
- URL routing issues - clinic slug not working?
- Middleware not setting context?

**Solution:** Check MULTITENANT_IMPLEMENTATION.md or MIGRATION_GUIDE.md

---

**Remember:** The middleware + manager pattern = automatic data isolation ✅

**Golden Rule:** Always verify `get_current_clinic()` returns correct clinic before querying!
