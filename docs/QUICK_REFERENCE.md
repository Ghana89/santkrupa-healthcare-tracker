# Multi-Tenant Quick Reference Card
## One-Page Implementation Cheat Sheet

---

## Core Architecture Pattern

```
┌─────────────────────────────────────────────┐
│  URL: /clinic/<clinic_slug>/patients/       │
├─────────────────────────────────────────────┤
│  TenantMiddleware (sets clinic context)     │
├─────────────────────────────────────────────┤
│  Request → View (checks request.clinic)     │
├─────────────────────────────────────────────┤
│  ClinicManager.filter(clinic=current)       │
├─────────────────────────────────────────────┤
│  Database (data partitioned by clinic_id)   │
└─────────────────────────────────────────────┘
```

---

## 5-Minute Implementation

### 1. Add Clinic Model (5 min)
```python
# hospital/models.py
class Clinic(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    # ... other fields ...
```

### 2. Update User Model (2 min)
```python
# hospital/models.py - Add to User model
clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)

class Meta:
    unique_together = [['clinic', 'username']]
```

### 3. Add clinic_id to Models (3 min)
```python
# hospital/models.py - Add to ALL models
clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)

class Meta:
    unique_together = [['clinic', 'patient_id']]  # Example for Patient
```

### 4. Create Manager (3 min)
```python
# hospital/managers.py
class ClinicManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            clinic=get_current_clinic()
        )

# In models.py
class Patient(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    # ... fields ...
    objects = ClinicManager()  # ✅ Use custom manager
```

### 5. Add Middleware (3 min)
```python
# hospital/middleware.py
import threading
_thread_locals = threading.local()

def get_current_clinic():
    return getattr(_thread_locals, 'clinic', None)

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        clinic_slug = request.resolver_match.kwargs.get('clinic_slug')
        clinic = Clinic.objects.get(slug=clinic_slug)
        _thread_locals.clinic = clinic
        return self.get_response(request)

# settings.py - Add to MIDDLEWARE
'hospital.middleware.TenantMiddleware',
```

### 6. Update URLs (2 min)
```python
# urls.py
path('clinic/<slug:clinic_slug>/', include([
    path('patients/', views.patient_list),
    # ... more URLs ...
]))
```

### 7. Update Views (2 min)
```python
# views.py
def patient_list(request, clinic_slug):
    clinic = get_current_clinic()
    # Queries auto-filtered by clinic via manager
    patients = Patient.objects.all()  # Returns only clinic's patients
    return render(request, 'patient_list.html', {'patients': patients})
```

---

## Critical Security Checks

```
✅ MUST DO:
├── [ ] clinic_id on EVERY model (no exceptions)
├── [ ] unique_together with clinic_id
├── [ ] Custom manager auto-filters
├── [ ] Middleware sets context
├── [ ] Views verify clinic match
├── [ ] Forms filter by clinic
├── [ ] Admin filters by clinic
└── [ ] Tests verify isolation

❌ NEVER DO:
├── [ ] Query without clinic filter
├── [ ] Assume clinic from session
├── [ ] Trust user input for clinic
├── [ ] Skip permission checks
├── [ ] Cache without clinic key
└── [ ] Join across clinics
```

---

## Common Patterns

### View Pattern
```python
@login_required
def patient_detail(request, clinic_slug, patient_id):
    clinic = get_current_clinic()
    # Verify user's clinic matches URL
    if request.user.clinic.slug != clinic_slug:
        raise PermissionDenied()
    # Get patient - auto-filtered by clinic via manager
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patient_detail.html', {'patient': patient})
```

### Form Pattern
```python
class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        clinic = get_current_clinic()
        # Filter choices to this clinic only
        self.fields['doctor'].queryset = Doctor.objects.filter(clinic=clinic)

    def clean(self):
        # Verify clinic assignment
        self.cleaned_data['clinic'] = get_current_clinic()
        return self.cleaned_data
```

### Query Pattern
```python
# ✅ CORRECT: Auto-filtered by manager
patients = Patient.objects.all()

# ✅ ALSO CORRECT: Explicit filtering
patients = Patient.objects.filter(clinic=clinic)

# ❌ WRONG: No clinic filter
patients = Patient.objects.raw("SELECT * FROM hospital_patient")
```

### Admin Pattern
```python
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        # Filter by user's clinic
        return super().get_queryset(request).filter(clinic=request.user.clinic)
    
    def save_model(self, request, obj, form, change):
        # Auto-set clinic
        obj.clinic = request.user.clinic
        super().save_model(request, obj, form, change)
```

---

## Database Indexes

```python
# hospital/models.py
class Patient(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['clinic', 'patient_id']),  # ✅ CRITICAL
            models.Index(fields=['clinic', 'phone_number']),
            models.Index(fields=['clinic', 'registration_date']),
        ]
```

---

## Testing Checklist

```python
def test_clinic_isolation():
    # Create two clinics
    clinic1 = Clinic.objects.create(name='Clinic 1', slug='clinic-1', ...)
    clinic2 = Clinic.objects.create(name='Clinic 2', slug='clinic-2', ...)
    
    # Create patients in each clinic
    patient1 = Patient.objects.create(clinic=clinic1, ...)
    patient2 = Patient.objects.create(clinic=clinic2, ...)
    
    # Verify clinic1 only sees their patient
    with set_current_clinic(clinic1):
        assert patient1 in Patient.objects.all()
        assert patient2 not in Patient.objects.all()
    
    # Verify clinic2 only sees their patient
    with set_current_clinic(clinic2):
        assert patient1 not in Patient.objects.all()
        assert patient2 in Patient.objects.all()
```

---

## Environment Variables (Production)

```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=santkrupa_hospital
DB_USER=django_user
DB_PASSWORD=strong_password_here
DB_HOST=db.example.com
DB_PORT=5432

# Redis
REDIS_URL=redis://redis.example.com:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password-here
EMAIL_USE_TLS=True

# Sentry
SENTRY_DSN=https://your-key@sentry.io/project-id

# AWS (if using S3)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=clinic-bucket
```

---

## URL Patterns Reference

```
/clinic/<slug>/                           → Clinic dashboard
/clinic/<slug>/patients/                  → Patient list
/clinic/<slug>/patients/<id>/             → Patient detail
/clinic/<slug>/patients/new/              → Create patient
/clinic/<slug>/doctors/                   → Doctor list
/clinic/<slug>/consultations/             → Consultations
/clinic/<slug>/admin/                     → Admin panel
/clinic/<slug>/api/v1/patients/           → API: List patients
/clinic/<slug>/api/v1/patients/<id>/      → API: Patient detail
```

---

## Deployment Checklist

```
BEFORE PRODUCTION:
└── [ ] Database migration tested
    ├── [ ] Backup taken
    ├── [ ] Migrate on staging first
    ├── [ ] Verify data integrity
    ├── [ ] Test all views
    └── [ ] Performance baseline

INFRASTRUCTURE:
└── [ ] PostgreSQL 13+ running
    ├── [ ] Redis configured
    ├── [ ] Nginx reverse proxy
    ├── [ ] SSL/TLS certificates
    ├── [ ] Gunicorn/uWSGI workers
    └── [ ] Celery workers

MONITORING:
└── [ ] Sentry configured
    ├── [ ] Logging enabled
    ├── [ ] Alerts configured
    ├── [ ] Backup scheduled
    ├── [ ] Health checks setup
    └── [ ] Performance metrics
```

---

## Common Errors & Fixes

```
ERROR: clinic_id NULL for existing records
FIX: Run data migration to assign default clinic
  python manage.py makemigrations --empty hospital --name assign_clinic
  # Then add RunPython step

ERROR: Queries returning data from other clinics
FIX: Verify ClinicManager is used
  # Check: objects = ClinicManager() in model
  # OR: Change default manager

ERROR: Middleware not setting context
FIX: Verify middleware in settings
  # Check: 'hospital.middleware.TenantMiddleware' in MIDDLEWARE
  # Check: After AuthenticationMiddleware

ERROR: Static files 404
FIX: Collect and verify paths
  python manage.py collectstatic --noinput
  # Check Nginx config paths

ERROR: Permission denied on file uploads
FIX: Set correct permissions
  chmod -R 755 media/
  chmod -R 755 staticfiles/
```

---

## Performance Tips

```
✅ OPTIMIZE:
├── [ ] Use select_related() for ForeignKey
├── [ ] Use prefetch_related() for reverse relations
├── [ ] Add database indexes on clinic_id
├── [ ] Cache querysets with Redis
├── [ ] Use async tasks for heavy processing
├── [ ] Paginate large result sets
└── [ ] Use database connection pooling

EXAMPLE:
# Without optimization (N+1 queries)
patients = Patient.objects.all()
for patient in patients:
    print(patient.clinic.name)  # Query for each patient!

# With optimization
patients = Patient.objects.select_related('clinic').all()
for patient in patients:
    print(patient.clinic.name)  # No extra queries!
```

---

## File Structure

```
hospital/
├── migrations/           # Database migrations
│   └── 000X_*.py        # Include clinic_id additions
├── templates/
│   └── hospital/
│       └── clinic/
│           ├── dashboard.html
│           ├── patients/
│           ├── doctors/
│           └── admin/
├── models.py            # ✅ Add clinic_id to ALL
├── views.py             # ✅ Add clinic filtering
├── forms.py             # ✅ Add clinic validation
├── managers.py          # ✅ NEW: ClinicManager
├── middleware.py        # ✅ NEW: TenantMiddleware
├── admin.py             # ✅ Update with filtering
├── urls.py              # ✅ Update with clinic_slug
├── tests.py             # ✅ Add multi-tenancy tests
├── serializers.py       # ✅ NEW: DRF serializers
└── api/
    ├── viewsets.py      # ✅ NEW: API endpoints
    └── permissions.py   # ✅ NEW: Permission classes

santkrupa_hospital/
├── settings.py          # ✅ Update
├── urls.py              # ✅ Update with clinic
├── wsgi.py
└── celery.py            # ✅ NEW (if using)
```

---

## Quick Setup Script

```bash
#!/bin/bash
# setup_multitenant.sh

# 1. Create managers.py
cat > hospital/managers.py << 'EOF'
# [Copy from IMPLEMENTATION_GUIDE_MULTITENANT.md]
EOF

# 2. Create middleware.py
cat > hospital/middleware.py << 'EOF'
# [Copy from IMPLEMENTATION_GUIDE_MULTITENANT.md]
EOF

# 3. Create migrations
python manage.py makemigrations

# 4. Run migrations
python manage.py migrate

# 5. Create test clinic
python manage.py shell << 'EOF'
from hospital.models import Clinic
Clinic.objects.create(
    name='Test Clinic',
    slug='test-clinic',
    email='test@clinic.com',
    phone_number='1234567890',
    address='Test Address',
    city='Test City',
    state='Test State',
    zip_code='123456',
    registration_number='REG-123456',
    gstin='GSTIN123456',
)
print("✅ Setup complete!")
EOF

# 6. Run tests
python manage.py test
```

---

## Reference Links

- [Django Multi-Tenancy Best Practices](https://django-tenants.readthedocs.io/)
- [PostgreSQL Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Django ORM Select/Prefetch](https://docs.djangoproject.com/en/5.0/topics/db/optimization/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Last Updated: February 8, 2026**
**Status: Ready to Implement**
**Difficulty: Moderate → Advanced**

