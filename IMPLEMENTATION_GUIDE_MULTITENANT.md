# Multi-Tenant Implementation Guide
## Refactoring Existing Django Code for Clinic Isolation

---

## 1. Critical Changes Needed

### 1.1 Model Updates Required

Your current models lack clinic isolation. Here's what needs to change:

#### **Current Issues:**
```python
# ❌ WRONG: No clinic_id - data from multiple clinics mixed
class Patient(models.Model):
    patient_name = models.CharField(max_length=100)
    # No clinic_id field - SECURITY ISSUE!
```

#### **Solution:**
```python
# ✅ CORRECT: Every model must have clinic_id
class Patient(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    # ... other fields ...
    
    class Meta:
        unique_together = [['clinic', 'patient_id']]  # Unique per clinic
```

### 1.2 Implementation Steps

#### **Step 1: Create Clinic Model** (New)
```python
# Add to hospital/models.py

class Clinic(models.Model):
    """Multi-tenant clinic model"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Used in URLs: /clinic/{slug}/")
    logo = models.ImageField(upload_to='clinic_logos/', null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(null=True, blank=True)
    registration_number = models.CharField(max_length=100, unique=True)
    gstin = models.CharField(max_length=15, unique=True)
    
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
        ],
        default='trial'
    )
    
    max_doctors = models.IntegerField(default=10)
    max_patients = models.IntegerField(default=1000)
    max_receptionists = models.IntegerField(default=5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Clinics"
    
    def __str__(self):
        return self.name
```

#### **Step 2: Update User Model** (Critical)
```python
# Modify existing User model in hospital/models.py

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),  # NEW: Platform owner
        ('admin', 'Clinic Admin'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('patient', 'Patient'),
        ('lab_tech', 'Lab Technician'),
    ]
    
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['clinic', 'username']]  # Username unique per clinic
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.clinic.name}"
```

#### **Step 3: Update Patient Model** (Critical)
```python
# Replace existing Patient model

class Patient(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('in_diagnosis', 'In Diagnosis'),
        ('treatment_started', 'Treatment Started'),
        ('discharged', 'Discharged'),
    ]
    
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD THIS
    patient_id = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    identification_type = models.CharField(max_length=50)
    identification_number = models.CharField(max_length=100)
    
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='patients_registered',
                                     limit_choices_to={'role': 'receptionist'})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-registration_date']
        unique_together = [['clinic', 'patient_id']]  # ✅ Unique per clinic
        indexes = [
            models.Index(fields=['clinic', 'registration_date']),
            models.Index(fields=['clinic', 'phone_number']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self.generate_patient_id()
        super().save(*args, **kwargs)
    
    def generate_patient_id(self):
        """Generate unique patient ID per clinic"""
        from django.utils import timezone
        import random
        # PT-<clinic_id>-<year>-<random>
        prefix = f"PT{self.clinic.id}"
        year = timezone.now().year
        rand = random.randint(10000, 99999)
        return f"{prefix}-{year}-{rand}"
    
    def __str__(self):
        return f"{self.patient_name} ({self.patient_id}) - {self.clinic.name}"
```

#### **Step 4: Add clinic_id to ALL Models**

```python
# Example for other models - add clinic field to each

class Doctor(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    
    class Meta:
        unique_together = [['clinic', 'license_number']]  # ✅ ADD
    
    def __str__(self):
        return f"Dr. {self.user.first_name} - {self.clinic.name}"


class Prescription(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True,
                              related_name='prescriptions')
    # ... rest of fields ...


class PatientVisit(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    # ... rest of fields ...


class MedicalReport(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    # ... rest of fields ...


class TestReport(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)  # ✅ ADD
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_reports')
    # ... rest of fields ...
```

---

## 2. QuerySet Filtering (Critical Security)

### 2.1 Custom Manager for Auto-Filtering

```python
# Add to hospital/models.py

from django.db import models
from django.core.exceptions import ImproperlyConfigured

class ClinicQuerySet(models.QuerySet):
    """QuerySet that automatically filters by current clinic"""
    
    def for_clinic(self, clinic):
        """Filter queryset for specific clinic"""
        if not clinic:
            raise ImproperlyConfigured("Clinic context is required")
        return self.filter(clinic=clinic)


class ClinicManager(models.Manager):
    """Manager that filters by current clinic"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Get clinic from thread-local or request context
        clinic = self.get_current_clinic()
        if clinic:
            return qs.filter(clinic=clinic)
        return qs
    
    def get_current_clinic(self):
        """Extract clinic from thread-local context"""
        from django.core.exceptions import ImproperlyConfigured
        from .middleware import get_current_clinic
        
        clinic = get_current_clinic()
        if not clinic:
            raise ImproperlyConfigured(
                "Clinic context not set. Make sure TenantMiddleware is installed."
            )
        return clinic
    
    def for_clinic(self, clinic):
        """Get queryset for specific clinic"""
        return self.filter(clinic=clinic)


# Update models to use custom manager
class Patient(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    # ... fields ...
    
    objects = ClinicManager()  # ✅ Auto-filters by clinic
    
    def __str__(self):
        return f"{self.patient_name} ({self.patient_id})"
```

### 2.2 Middleware for Tenant Context

```python
# Create hospital/middleware.py

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
    Middleware to set clinic context from:
    1. URL parameter (clinic_slug)
    2. Session
    3. User's default clinic
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract clinic from URL
        clinic_slug = request.resolver_match.kwargs.get('clinic_slug') if request.resolver_match else None
        
        if clinic_slug:
            from .models import Clinic
            try:
                clinic = Clinic.objects.get(slug=clinic_slug)
                set_current_clinic(clinic)
                request.clinic = clinic
            except Clinic.DoesNotExist:
                set_current_clinic(None)
                request.clinic = None
        elif request.user.is_authenticated:
            # Use user's default clinic
            if hasattr(request.user, 'clinic'):
                set_current_clinic(request.user.clinic)
                request.clinic = request.user.clinic
        else:
            set_current_clinic(None)
            request.clinic = None
        
        set_current_user(request.user)
        
        try:
            response = self.get_response(request)
        finally:
            # Clean up thread-local storage
            set_current_clinic(None)
            set_current_user(AnonymousUser())
        
        return response
```

### 2.3 Update Settings

```python
# Add to santkrupa_hospital/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'hospital.middleware.TenantMiddleware',  # ✅ ADD THIS
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

## 3. URL Routing Changes

### 3.1 Update URL Configuration

```python
# santkrupa_hospital/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Clinic-specific URLs
    path('clinic/<slug:clinic_slug>/', include([
        path('admin/', admin.site.urls),
        path('', include('hospital.urls')),  # Your hospital app URLs
    ])),
    
    # Platform-wide URLs (before clinic)
    path('api/auth/', include('hospital.api.auth')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3.2 Update hospital/urls.py

```python
# hospital/urls.py

from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.create_patient, name='create_patient'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Doctor URLs
    path('doctor/queue/', views.doctor_queue, name='doctor_queue'),
    path('doctor/consultation/<int:patient_id>/', views.consultation, name='consultation'),
    
    # Receptionist URLs
    path('receptionist/checkin/', views.patient_checkin, name='patient_checkin'),
    
    # Admin URLs
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/settings/', views.clinic_settings, name='clinic_settings'),
]
```

---

## 4. Views & Forms Updates

### 4.1 View Pattern with Clinic Filtering

```python
# hospital/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Patient, Clinic
from .middleware import get_current_clinic


@login_required
def patient_list(request, clinic_slug):
    """List patients for current clinic only"""
    clinic = get_current_clinic()
    
    # SECURITY CHECK: User's clinic must match URL clinic
    if request.user.clinic.slug != clinic_slug:
        raise PermissionDenied("Access denied")
    
    # Query filters by clinic automatically via manager
    patients = Patient.objects.for_clinic(clinic)
    
    context = {
        'patients': patients,
        'clinic': clinic,
    }
    return render(request, 'hospital/patient_list.html', context)


@login_required
def create_patient(request, clinic_slug):
    """Create new patient (receptionist only)"""
    clinic = get_current_clinic()
    
    # RBAC Check
    if request.user.role not in ['admin', 'receptionist']:
        raise PermissionDenied("Only receptionists can create patients")
    
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.clinic = clinic  # ✅ Set clinic automatically
            patient.registered_by = request.user
            patient.save()
            return redirect('hospital:patient_detail', 
                          clinic_slug=clinic_slug, 
                          patient_id=patient.id)
    else:
        form = PatientForm()
    
    return render(request, 'hospital/create_patient.html', {
        'form': form,
        'clinic': clinic,
    })


@login_required
def patient_detail(request, clinic_slug, patient_id):
    """View patient details"""
    clinic = get_current_clinic()
    
    # Get patient and ensure they belong to this clinic
    patient = get_object_or_404(Patient, clinic=clinic, id=patient_id)
    
    context = {
        'patient': patient,
        'clinic': clinic,
    }
    return render(request, 'hospital/patient_detail.html', context)
```

### 4.2 Form with Clinic Filtering

```python
# hospital/forms.py

from django import forms
from .models import Patient, Doctor, Prescription
from .middleware import get_current_clinic


class PatientForm(forms.ModelForm):
    """Form for patient creation with clinic isolation"""
    
    class Meta:
        model = Patient
        fields = [
            'patient_name', 'date_of_birth', 'gender', 'blood_group',
            'phone_number', 'email', 'address', 'city', 'state', 'zip_code',
            'emergency_contact_name', 'emergency_contact_phone',
            'identification_type', 'identification_number',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get current clinic
        clinic = get_current_clinic()
        
        # Filter choices by clinic
        self.fields['registered_by'].queryset = \
            Doctor.objects.filter(clinic=clinic)


class PrescriptionForm(forms.ModelForm):
    """Form for prescription creation"""
    
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'notes']
    
    def __init__(self, *args, **kwargs):
        clinic = get_current_clinic()
        super().__init__(*args, **kwargs)
        
        # ✅ Filter by clinic
        self.fields['patient'].queryset = \
            Patient.objects.filter(clinic=clinic)
        self.fields['doctor'].queryset = \
            Doctor.objects.filter(clinic=clinic)
```

---

## 5. File Storage Isolation

### 5.1 Clinic-Specific File Paths

```python
# hospital/utils/file_upload.py

import os
from django.conf import settings
from .middleware import get_current_clinic


def get_clinic_media_path(instance, filename):
    """Generate clinic-specific file path"""
    clinic = get_current_clinic()
    if not clinic:
        clinic = instance.clinic
    
    # Path: media/clinic_<clinic_id>/<model_name>/<filename>
    return f'clinic_{clinic.id}/{instance.__class__.__name__}/{filename}'


# Usage in model
class MedicalReport(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    report_file = models.FileField(
        upload_to=get_clinic_media_path  # ✅ Clinic-specific path
    )


class TestReport(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    report_file = models.FileField(
        upload_to=get_clinic_media_path  # ✅ Clinic-specific path
    )
```

### 5.2 Settings Configuration

```python
# santkrupa_hospital/settings.py

# Media files storage
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# For production with S3
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = 'healthcare-app-bucket'
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
```

---

## 6. Admin Interface Customization

### 6.1 Admin with Clinic Filtering

```python
# hospital/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Clinic, User, Patient, Doctor, Prescription
from .middleware import get_current_clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subscription_status', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['subscription_status', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'patient_id', 'clinic', 'phone_number', 'registration_date']
    list_filter = ['clinic', 'status', 'registration_date']
    search_fields = ['patient_name', 'patient_id', 'phone_number']
    readonly_fields = ['patient_id', 'clinic', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Filter by clinic if user is clinic-specific"""
        qs = super().get_queryset(request)
        
        if not request.user.is_superuser:
            # Filter by user's clinic
            qs = qs.filter(clinic=request.user.clinic)
        
        return qs
    
    def save_model(self, request, obj, form, change):
        """Auto-set clinic on creation"""
        if not change:  # Creating new object
            obj.clinic = request.user.clinic
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'clinic', 'license_number']
    list_filter = ['clinic', 'specialization']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    
    def get_full_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Doctor Name'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(clinic=request.user.clinic)
        return qs


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_doctor_name', 'clinic', 'prescription_date']
    list_filter = ['clinic', 'status', 'prescription_date']
    search_fields = ['patient__patient_name', 'doctor__user__first_name']
    
    def get_patient_name(self, obj):
        return obj.patient.patient_name
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name}"
    get_doctor_name.short_description = 'Doctor'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(clinic=request.user.clinic)
        return qs
```

---

## 7. Migrations Strategy

### 7.1 Create Migration for Clinic Model

```bash
# In terminal
cd c:\Users\ADMIN\Documents\healthcare\santkrupa-healthcare-tracker

# 1. Make migration for adding Clinic model
python manage.py makemigrations hospital --name "add_clinic_model"

# 2. Make migration for adding clinic_id to existing models
python manage.py makemigrations hospital --name "add_clinic_foreign_keys"

# 3. Create data migration to assign existing records to default clinic
python manage.py makemigrations hospital --name "assign_clinic_to_existing_records"

# 4. Apply migrations
python manage.py migrate hospital
```

### 7.2 Data Migration for Existing Records

```python
# hospital/migrations/0003_assign_clinic_to_existing_records.py

from django.db import migrations

def assign_clinic_to_existing(apps, schema_editor):
    """Assign all existing records to a default clinic"""
    Clinic = apps.get_model('hospital', 'Clinic')
    Patient = apps.get_model('hospital', 'Patient')
    Doctor = apps.get_model('hospital', 'Doctor')
    User = apps.get_model('hospital', 'User')
    
    # Create default clinic
    default_clinic, created = Clinic.objects.get_or_create(
        name='Default Clinic',
        defaults={
            'slug': 'default-clinic',
            'email': 'admin@default-clinic.com',
            'phone_number': '0000000000',
            'address': 'Default Address',
            'city': 'Unknown',
            'state': 'Unknown',
            'zip_code': '000000',
            'registration_number': 'REG-000000',
            'gstin': 'GSTIN000000',
        }
    )
    
    # Assign to all existing users
    User.objects.filter(clinic__isnull=True).update(clinic=default_clinic)
    
    # Assign to all existing patients
    Patient.objects.filter(clinic__isnull=True).update(clinic=default_clinic)
    
    # Assign to all existing doctors
    Doctor.objects.filter(clinic__isnull=True).update(clinic=default_clinic)


def reverse_migration(apps, schema_editor):
    """Reverse the migration"""
    Clinic = apps.get_model('hospital', 'Clinic')
    Clinic.objects.filter(slug='default-clinic').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('hospital', '0002_add_clinic_foreign_keys'),
    ]
    
    operations = [
        migrations.RunPython(assign_clinic_to_existing, reverse_migration),
    ]
```

---

## 8. Testing Multi-Tenancy

### 8.1 Test Case Template

```python
# hospital/tests.py

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Clinic, Patient, Doctor


class MultiTenancyTestCase(TestCase):
    """Test multi-tenant isolation"""
    
    def setUp(self):
        """Create test clinics and users"""
        User = get_user_model()
        
        # Create clinic 1
        self.clinic1 = Clinic.objects.create(
            name='Clinic 1',
            slug='clinic-1',
            email='clinic1@test.com',
            phone_number='1111111111',
            address='Address 1',
            city='City 1',
            state='State 1',
            zip_code='111111',
            registration_number='REG-111111',
            gstin='GSTIN111111',
        )
        
        # Create clinic 2
        self.clinic2 = Clinic.objects.create(
            name='Clinic 2',
            slug='clinic-2',
            email='clinic2@test.com',
            phone_number='2222222222',
            address='Address 2',
            city='City 2',
            state='State 2',
            zip_code='222222',
            registration_number='REG-222222',
            gstin='GSTIN222222',
        )
        
        # Create admin user for clinic 1
        self.user1 = User.objects.create_user(
            username='admin1',
            password='testpass123',
            clinic=self.clinic1,
            role='admin'
        )
        
        # Create admin user for clinic 2
        self.user2 = User.objects.create_user(
            username='admin2',
            password='testpass123',
            clinic=self.clinic2,
            role='admin'
        )
        
        # Create patient in clinic 1
        self.patient1 = Patient.objects.create(
            clinic=self.clinic1,
            patient_name='Patient 1',
            date_of_birth='1990-01-01',
            gender='M',
            phone_number='9999999999',
            address='Address',
            city='City',
            state='State',
            zip_code='000000',
            emergency_contact_name='Contact',
            emergency_contact_phone='8888888888',
            identification_type='Aadhaar',
            identification_number='123456789012',
        )
        
        # Create patient in clinic 2
        self.patient2 = Patient.objects.create(
            clinic=self.clinic2,
            patient_name='Patient 2',
            date_of_birth='1991-01-01',
            gender='F',
            phone_number='8888888888',
            address='Address',
            city='City',
            state='State',
            zip_code='000000',
            emergency_contact_name='Contact',
            emergency_contact_phone='9999999999',
            identification_type='PAN',
            identification_number='ABCDE1234F',
        )
    
    def test_clinic_isolation_patients(self):
        """Test that clinic1 patient not accessible from clinic2"""
        # Clinic 1 should only see their own patients
        patients_clinic1 = Patient.objects.for_clinic(self.clinic1)
        self.assertIn(self.patient1, patients_clinic1)
        self.assertNotIn(self.patient2, patients_clinic1)
        
        # Clinic 2 should only see their own patients
        patients_clinic2 = Patient.objects.for_clinic(self.clinic2)
        self.assertNotIn(self.patient1, patients_clinic2)
        self.assertIn(self.patient2, patients_clinic2)
    
    def test_user_clinic_assignment(self):
        """Test user belongs to correct clinic"""
        self.assertEqual(self.user1.clinic, self.clinic1)
        self.assertEqual(self.user2.clinic, self.clinic2)
    
    def test_patient_unique_id_per_clinic(self):
        """Test patient IDs are unique per clinic, not globally"""
        # Two different clinics can have same patient ID
        patient_clinic1 = Patient.objects.create(
            clinic=self.clinic1,
            patient_id='PT1-2024-10001',
            patient_name='Test Patient 1',
            date_of_birth='1990-01-01',
            gender='M',
            phone_number='1111111111',
            address='Address',
            city='City',
            state='State',
            zip_code='000000',
            emergency_contact_name='Contact',
            emergency_contact_phone='2222222222',
            identification_type='Aadhaar',
            identification_number='111111111111',
        )
        
        patient_clinic2 = Patient.objects.create(
            clinic=self.clinic2,
            patient_id='PT1-2024-10001',  # Same ID, different clinic
            patient_name='Test Patient 2',
            date_of_birth='1991-01-01',
            gender='F',
            phone_number='3333333333',
            address='Address',
            city='City',
            state='State',
            zip_code='000000',
            emergency_contact_name='Contact',
            emergency_contact_phone='4444444444',
            identification_type='PAN',
            identification_number='ABCDE1234G',
        )
        
        # Both should exist (unique per clinic, not global)
        self.assertEqual(patient_clinic1.patient_id, patient_clinic2.patient_id)
```

---

## 9. Verification Checklist

- [ ] Clinic model created
- [ ] All models have clinic_id foreign key
- [ ] Custom manager with auto-filtering implemented
- [ ] TenantMiddleware added to settings
- [ ] URL routing includes clinic_slug parameter
- [ ] All views filter by current clinic
- [ ] All forms filtered by clinic
- [ ] Admin interface respects clinic boundaries
- [ ] File storage organized by clinic
- [ ] Migrations created and applied
- [ ] Tests passing (multi-tenancy test cases)
- [ ] Cross-clinic data access prevented
- [ ] User cannot access other clinic's data

---

## 10. Next Steps

1. **Backup Database**: Before making changes, backup existing SQLite database
2. **Review Changes**: Go through each section and understand the changes
3. **Implement Incrementally**: Make changes module by module
4. **Test Thoroughly**: Run tests after each major change
5. **Deploy to Staging**: Test in staging environment first
6. **Deploy to Production**: With proper backup and rollback plan

