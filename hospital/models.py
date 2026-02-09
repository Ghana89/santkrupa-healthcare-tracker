from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import random
import string
from .managers import ClinicManager, get_current_clinic

# ============================================================================
# CLINIC MODEL - Multi-Tenant Foundation
# ============================================================================

class Clinic(models.Model):
    """
    Represents a hospital/clinic.
    All other models use clinic_id to partition data.
    """
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
        return f"{self.name} ({self.slug})"


# ============================================================================
# USER MODEL - Updated with Clinic
# ============================================================================

# Custom User model to differentiate roles
class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Clinic Admin'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('patient', 'Patient'),
        ('lab_tech', 'Lab Technician'),
    ]
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['clinic', 'username']]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.clinic.name}"

# Patient model
class Patient(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('in_diagnosis', 'In Diagnosis'),
        ('treatment_started', 'Treatment Started'),
        ('discharged', 'Discharged'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    patient_id = models.CharField(max_length=20, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    default_password = models.CharField(max_length=20, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='patients_registered', 
                                     limit_choices_to={'role': 'receptionist'})
    
    # Use custom manager for auto-filtering
    objects = ClinicManager()
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self.generate_patient_id()
        if not self.default_password:
            self.default_password = self.generate_default_password()
        super().save(*args, **kwargs)
    
    def generate_patient_id(self):
        """Generate unique patient ID per clinic"""
        prefix = f"PT{self.clinic.id}"
        year = timezone.now().year
        rand = random.randint(10000, 99999)
        return f"{prefix}-{year}-{rand}"
    
    def generate_default_password(self):
        """Generate default password for patient"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def __str__(self):
        return f"{self.patient_name} ({self.patient_id}) - {self.clinic.name}"
    
    class Meta:
        ordering = ['-registration_date']
        unique_together = [['clinic', 'patient_id']]
        indexes = [
            models.Index(fields=['clinic', 'registration_date']),
            models.Index(fields=['clinic', 'phone_number']),
        ]

# Doctor model
class Doctor(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    
    objects = ClinicManager()
    
    class Meta:
        unique_together = [['clinic', 'license_number']]
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.clinic.name}"

# Prescription model (Doctor prescribes tests and medicines)
class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, 
                              related_name='prescriptions')
    prescription_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"Prescription for {self.patient.patient_name} by Dr. {self.doctor.user.first_name}"
    
    class Meta:
        ordering = ['-prescription_date']

# Test model
class Test(models.Model):
    TEST_TYPES = [
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('other', 'Other'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='tests', null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    test_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_date = models.DateField(null=True, blank=True)
    result = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.test_name} for {self.prescription.patient.patient_name}"

# Medicine model
class Medicine(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='medicines', null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "Twice a day", "Once daily"
    duration = models.CharField(max_length=100)   # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"

# Doctor Thoughts/Notes
class DoctorNotes(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctor_notes', null=True, blank=True)
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='doctor_notes')
    observations = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"Notes for {self.prescription.patient.patient_name}"

# Medical Report model
class MedicalReport(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='medical_reports', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    report_file = models.FileField(upload_to='medical_reports/')
    report_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"Report for {self.patient.patient_name}"
    
    class Meta:
        ordering = ['-uploaded_at']

# Patient Visit/Check-in model - to track each visit
class PatientVisit(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patient_visits', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                      limit_choices_to={'role': 'receptionist'},
                                      related_name='checked_in_patients')
    check_in_date = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=200, blank=True)  # e.g., "Checkup", "Follow-up", "Emergency"
    status = models.CharField(
        max_length=20,
        choices=[('checked_in', 'Checked In'), ('in_consultation', 'In Consultation'), 
                 ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='checked_in'
    )
    notes = models.TextField(blank=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.patient.patient_name} - {self.check_in_date.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-check_in_date']


# Test Report model - for uploading lab/test reports
class TestReport(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='test_reports', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_reports')
    test_type = models.CharField(max_length=100)  # e.g., "Blood Test", "X-Ray", "Ultrasound"
    report_file = models.FileField(upload_to='test_reports/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='uploaded_test_reports')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    test_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.test_type} - {self.patient.patient_name}"
    
    class Meta:
        ordering = ['-uploaded_at']
