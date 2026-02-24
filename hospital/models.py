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
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='prescriptions')

    prescription_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admission Recommendation
    admission_recommended = models.BooleanField(default=False, help_text="Doctor recommends patient admission to hospital")
    admission_reason = models.TextField(blank=True, help_text="Reason for recommending admission")
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"Prescription for {self.patient.patient_name} by Dr. {self.doctor.user.first_name}"
    
    class Meta:
        ordering = ['-prescription_date']

#Vitals model - to store patient's vitals during consultation or admission
class Vitals(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='vitals')

    bp = models.CharField(max_length=20, blank=True, null=True)
    pulse = models.CharField(max_length=20, blank=True, null=True)
    temp = models.CharField(max_length=20, blank=True, null=True)
    spo2 = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = ClinicManager()

    def __str__(self):
        return f"Vitals for {self.prescription.patient.patient_name}"
    
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
    
    @property
    def file_exists(self):
        """Check if the uploaded file exists"""
        import os
        if self.report_file:
            return os.path.exists(self.report_file.path)
        return False
    
    @property
    def file_name(self):
        """Get the original file name"""
        if self.report_file:
            return self.report_file.name.split('/')[-1]
        return 'Unknown'
    
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

# ============================================================================
# MASTER DATA MODELS - Medicine & Test Templates
# ============================================================================

class MasterMedicine(models.Model):
    """
    Master template for medicines per clinic.
    Doctors select from these when creating prescriptions.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='master_medicines', null=True, blank=True)
    medicine_name = models.CharField(max_length=200)
    dosage_options = models.TextField(help_text="Comma-separated list: e.g., '500mg, 1000mg, 2000mg'")
    frequency_options = models.TextField(help_text="Comma-separated list: e.g., 'Once daily, Twice daily, Thrice daily'")
    default_frequency = models.CharField(max_length=100, blank=True, help_text="Default frequency suggestion")
    default_duration = models.CharField(max_length=100, blank=True, help_text="Default duration suggestion: e.g., '7 days'")
    category = models.CharField(max_length=100, blank=True, help_text="e.g., 'Antibiotic, Pain Reliever, etc.'")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = ClinicManager()
    
    class Meta:
        ordering = ['medicine_name']
        unique_together = [['clinic', 'medicine_name']]
    
    def __str__(self):
        return f"{self.medicine_name} - {self.clinic.name}"


class MasterTest(models.Model):
    """
    Master template for tests per clinic.
    Doctors select from these when creating prescriptions.
    """
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
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='master_tests', null=True, blank=True)
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True, help_text="e.g., 'Cardiology, Pathology, etc.'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = ClinicManager()
    
    class Meta:
        ordering = ['test_type', 'test_name']
        unique_together = [['clinic', 'test_name']]
    
    def __str__(self):
        return f"{self.test_name} ({self.get_test_type_display()}) - {self.clinic.name}"


# ============================================================================
# ADMISSION & HOSPITALIZATION MODELS
# ============================================================================

class PatientAdmission(models.Model):
    """
    Track patient admission to hospital/ICU
    """
    ADMISSION_TYPES = [
        ('general', 'General Ward'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('day_care', 'Day Care'),
        ('isolation', 'Isolation Ward'),
    ]
    
    DISCHARGE_STATUS = [
        ('admitted', 'Admitted'),
        ('in_treatment', 'In Treatment'),
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('ready_for_discharge', 'Ready for Discharge'),
        ('discharged', 'Discharged'),
        ('shifted', 'Shifted to Another Facility'),
        ('deceased', 'Deceased'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patient_admissions', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='admissions')
    
    admission_date = models.DateTimeField(auto_now_add=True)
    admission_type = models.CharField(max_length=50, choices=ADMISSION_TYPES, default='general')
    bed_number = models.CharField(max_length=50, blank=True, help_text="e.g., 'ICU-5', 'Ward-A-12'")
    room_number = models.CharField(max_length=50, blank=True)
    
    reason_for_admission = models.TextField(help_text="Chief complaint, symptoms")
    medical_history = models.TextField(blank=True, help_text="Relevant past medical history")
    allergies = models.TextField(blank=True, help_text="Drug allergies, food allergies, etc.")
    
    status = models.CharField(max_length=30, choices=DISCHARGE_STATUS, default='admitted')
    
    discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.patient.patient_name} - Admitted on {self.admission_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-admission_date']


class TreatmentLog(models.Model):
    """
    Track treatments/procedures/medications given during admission
    """
    TREATMENT_TYPES = [
        ('medication', 'Medication'),
        ('injection', 'Injection'),
        ('saline', 'Saline/IV Fluid'),
        ('oxygen', 'Oxygen Therapy'),
        ('procedure', 'Procedure/Surgery'),
        ('monitoring', 'Monitoring'),
        ('therapy', 'Physical Therapy'),
        ('other', 'Other'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatment_logs', null=True, blank=True)
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='treatment_logs')
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       limit_choices_to={'role__in': ['doctor']},
                                       related_name='administered_treatments')
    
    treatment_type = models.CharField(max_length=50, choices=TREATMENT_TYPES)
    treatment_name = models.CharField(max_length=200, help_text="Name of medication, injection, procedure, etc.")
    description = models.TextField(blank=True)
    
    # For medications/injections
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=100, blank=True, help_text="e.g., 'IV', 'IM', 'Oral', 'Inhalation'")
    
    # For saline/IV
    saline_type = models.CharField(max_length=100, blank=True, help_text="e.g., 'Normal Saline (0.9%)', 'D5W', 'Ringer\'s Lactate'")
    quantity = models.CharField(max_length=100, blank=True, help_text="e.g., '500ml', '1L'")
    
    # For oxygen
    oxygen_flow_rate = models.CharField(max_length=100, blank=True, help_text="e.g., '2L/min', '60%'")
    oxygen_type = models.CharField(max_length=100, blank=True, help_text="e.g., 'Nasal Cannula', 'Mask', 'Ventilator'")
    
    # General
    administered_date = models.DateTimeField()
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., '30 mins', '2 hours'")
    notes = models.TextField(blank=True, help_text="Observations, patient response, any complications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ClinicManager()
    
    def __str__(self):
        return f"{self.get_treatment_type_display()} - {self.treatment_name}"
    
    class Meta:
        ordering = ['-administered_date']
        indexes = [
            models.Index(fields=['admission', '-administered_date']),
            models.Index(fields=['clinic', '-administered_date']),
        ]