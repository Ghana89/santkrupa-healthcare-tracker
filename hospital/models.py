from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import random
import string

# Custom User model to differentiate roles
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)

# Patient model
class Patient(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('in_diagnosis', 'In Diagnosis'),
        ('treatment_started', 'Treatment Started'),
        ('discharged', 'Discharged'),
    ]
    
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
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
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self.generate_patient_id()
        if not self.default_password:
            self.default_password = self.generate_default_password()
        super().save(*args, **kwargs)
    
    def generate_patient_id(self):
        """Generate unique patient ID"""
        return f"PT{timezone.now().year}{random.randint(10000, 99999)}"
    
    def generate_default_password(self):
        """Generate default password for patient"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def __str__(self):
        return f"{self.patient_name} ({self.patient_id})"
    
    class Meta:
        ordering = ['-registration_date']

# Doctor model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"

# Prescription model (Doctor prescribes tests and medicines)
class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, 
                              related_name='prescriptions')
    prescription_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
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
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    test_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_date = models.DateField(null=True, blank=True)
    result = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.test_name} for {self.prescription.patient.patient_name}"

# Medicine model
class Medicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "Twice a day", "Once daily"
    duration = models.CharField(max_length=100)   # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"

# Doctor Thoughts/Notes
class DoctorNotes(models.Model):
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='doctor_notes')
    observations = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notes for {self.prescription.patient.patient_name}"

# Medical Report model
class MedicalReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    report_file = models.FileField(upload_to='medical_reports/')
    report_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Report for {self.patient.patient_name}"
    
    class Meta:
        ordering = ['-uploaded_at']

# Patient Visit/Check-in model - to track each visit
class PatientVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                      limit_choices_to={'role': 'receptionist'})
    check_in_date = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=200, blank=True)  # e.g., "Checkup", "Follow-up", "Emergency"
    status = models.CharField(
        max_length=20,
        choices=[('checked_in', 'Checked In'), ('in_consultation', 'In Consultation'), 
                 ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='checked_in'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.patient.patient_name} - {self.check_in_date.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-check_in_date']

# Test Report model - for uploading lab/test reports
class TestReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_reports')
    test_type = models.CharField(max_length=100)  # e.g., "Blood Test", "X-Ray", "Ultrasound"
    report_file = models.FileField(upload_to='test_reports/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    test_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.test_type} - {self.patient.patient_name}"
    
    class Meta:
        ordering = ['-uploaded_at']
