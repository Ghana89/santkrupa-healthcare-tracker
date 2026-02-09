from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Patient, MedicalReport, Prescription, Doctor, Test, Medicine, DoctorNotes, User, PatientVisit, TestReport, Clinic
from .forms import (PatientRegistrationForm, PrescriptionForm, TestForm, MedicineForm,
                    DoctorNotesForm, MedicalReportForm, DoctorUserCreationForm, 
                    ReceptionistUserCreationForm, DoctorProfileForm, PatientVisitForm, TestReportForm, ClinicRegistrationForm)
from django.utils.crypto import get_random_string


# ==================== HELPER FUNCTIONS ====================

def get_clinic_from_slug_or_middleware(clinic_slug, request):
    """
    Helper function to get clinic from URL slug or middleware context.
    
    Priority:
    1. clinic_slug parameter (if provided)
    2. request.clinic from middleware
    3. user.clinic (if authenticated)
    
    Returns: Clinic object or None
    """
    if clinic_slug:
        try:
            return Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            return None
    
    # Try request clinic from middleware
    if hasattr(request, 'clinic') and request.clinic:
        return request.clinic
    
    # Try user's clinic
    if request.user.is_authenticated and hasattr(request.user, 'clinic'):
        return request.user.clinic
    
    return None


# ==================== AUTHENTICATION VIEWS ====================

@require_http_methods(["GET", "POST"])
def login_view(request, clinic_slug=None):
    """User login"""
    if request.user.is_authenticated:
        # choose clinic slug preference: explicit param -> middleware -> user's clinic
        target_slug = None
        if clinic_slug:
            target_slug = clinic_slug
        elif hasattr(request, 'clinic') and request.clinic:
            target_slug = request.clinic.slug
        elif getattr(request.user, 'clinic', None):
            target_slug = request.user.clinic.slug

        if request.user.role == 'patient':
            if target_slug:
                return redirect('patient_dashboard', clinic_slug=target_slug)
            return redirect('patient_dashboard')
        elif request.user.role == 'doctor':
            if target_slug:
                return redirect('doctor_dashboard', clinic_slug=target_slug)
            return redirect('doctor_dashboard')
        elif request.user.role == 'receptionist':
            if target_slug:
                return redirect('reception_dashboard', clinic_slug=target_slug)
            return redirect('reception_dashboard')
        elif request.user.role == 'admin':
            if target_slug:
                return redirect('admin_dashboard', clinic_slug=target_slug)
            # no clinic context available — send to homepage to avoid reversing clinic-scoped URL without slug
            return redirect('homepage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            
            if next_url:
                return redirect(next_url)
            
            # Redirect to clinic-specific dashboards when clinic context exists
            clinic = getattr(request, 'clinic', None)
            # prefer clinic from request, then user's clinic
            target_clinic = clinic or getattr(user, 'clinic', None)

            if user.role == 'patient':
                if target_clinic:
                    return redirect('patient_dashboard', clinic_slug=target_clinic.slug)
                return redirect('patient_dashboard')
            elif user.role == 'doctor':
                if target_clinic:
                    return redirect('doctor_dashboard', clinic_slug=target_clinic.slug)
                return redirect('doctor_dashboard')
            elif user.role == 'receptionist':
                if target_clinic:
                    return redirect('reception_dashboard', clinic_slug=target_clinic.slug)
                return redirect('reception_dashboard')
            elif user.role == 'admin':
                if target_clinic:
                    return redirect('admin_dashboard', clinic_slug=target_clinic.slug)
                # avoid reversing clinic-scoped admin URL without slug
                return redirect('homepage')
            else:
                return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password.')
    
    context = {}
    return render(request, 'hospital/login.html', context)


@login_required(login_url='login')
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('homepage')

def homepage(request):
    """Homepage - Direct to appropriate role dashboard"""
    if request.user.is_authenticated:
        # Resolve clinic slug preference: middleware -> user's clinic
        clinic = getattr(request, 'clinic', None)
        target_slug = clinic.slug if clinic else (getattr(request.user, 'clinic', None).slug if getattr(request.user, 'clinic', None) else None)

        if request.user.role == 'patient':
            if target_slug:
                return redirect('patient_dashboard', clinic_slug=target_slug)
            return redirect('patient_dashboard')
        elif request.user.role == 'doctor':
            if target_slug:
                return redirect('doctor_dashboard', clinic_slug=target_slug)
            return redirect('doctor_dashboard')
        elif request.user.role == 'receptionist':
            if target_slug:
                return redirect('reception_dashboard', clinic_slug=target_slug)
            return redirect('reception_dashboard')
        elif request.user.role == 'admin':
            if target_slug:
                return redirect('admin_dashboard', clinic_slug=target_slug)
            # Keep admin on homepage if no clinic association to avoid reversing clinic-scoped URL
            # fallthrough to render platform homepage
    
    # Get clinic context (for clinic-specific homepage if accessed from clinic URL)
    clinic = getattr(request, 'clinic', None)
    clinics = Clinic.objects.filter(is_active=True).order_by('name')
    
    # Calculate statistics
    if clinic:
        # Clinic-specific statistics
        total_patients = Patient.objects.filter(clinic=clinic).count()
        total_doctors = Doctor.objects.filter(clinic=clinic).count()
    else:
        # Platform-wide statistics (for non-clinic users)
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
    
    total_clinics = clinics.count()

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_clinics': total_clinics,
        'clinics': clinics,
        'clinic': clinic,
    }
    return render(request, 'hospital/homepage.html', context)


@require_http_methods(["GET", "POST"])
def register_clinic(request):
    """Public clinic registration"""
    if request.method == 'POST':
        form = ClinicRegistrationForm(request.POST)
        if form.is_valid():
            clinic = form.save(commit=False)
            clinic.is_active = True
            clinic.save()
            # Auto-create a clinic admin account
            base_username = f"{clinic.slug}_admin".lower()
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{suffix}"
                suffix += 1

            password = get_random_string(10)
            admin_user = User.objects.create_user(
                username=username,
                password=password,
                email=clinic.email or '',
                clinic=clinic,
                role='admin',
            )
            admin_user.is_staff = True
            admin_user.save()

            messages.success(request, (
                f"Clinic '{clinic.name}' registered. "
                f"Admin account created: username='{username}', password='{password}'. "
                f"Login at /clinic/{clinic.slug}/login/ and change the password immediately."
            ))
            return redirect('homepage')
    else:
        form = ClinicRegistrationForm()

    return render(request, 'hospital/register_clinic.html', {'form': form})


# ==================== RECEPTION VIEWS ====================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def reception_dashboard(request, clinic_slug=None):
    """Reception person dashboard"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    # Resolve clinic: URL slug -> middleware -> user's clinic
    clinic = getattr(request, 'clinic', None)
    if not clinic and clinic_slug:
        try:
            clinic = Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            clinic = None
    if not clinic and getattr(request.user, 'clinic', None):
        clinic = request.user.clinic
    
    # Get clinic-specific patients
    patients = Patient.objects.filter(clinic=clinic).order_by('-registration_date') if clinic else Patient.objects.all().order_by('-registration_date')
    
    # Get today's check-ins (from PatientVisit)
    from django.utils import timezone
    today = timezone.now().date()
    todays_visits = PatientVisit.objects.filter(check_in_date__date=today, clinic=clinic).count() if clinic else PatientVisit.objects.filter(check_in_date__date=today).count()
    
    # Get pending prescriptions
    pending_prescriptions = Prescription.objects.filter(status='pending', clinic=clinic).count() if clinic else Prescription.objects.filter(status='pending').count()
    
    context = {
        'clinic': clinic,
        'patients': patients,
        'total_patients': patients.count(),
        'todays_visits': todays_visits,
        'pending_prescriptions': pending_prescriptions,
    }
    return render(request, 'hospital/reception/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def register_patient(request, clinic_slug=None):
    """Reception - Register new patient"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    # Get clinic context
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            if clinic:
                patient.clinic = clinic
            patient.save()
            
            messages.success(
                request,
                f"Patient {patient.patient_name} registered successfully! "
                f"Patient ID: {patient.patient_id}, Password: {patient.default_password}"
            )
            if clinic_slug:
                return redirect('reception_dashboard', clinic_slug=clinic_slug)
            return redirect('reception_dashboard')
    else:
        form = PatientRegistrationForm()
    
    context = {'form': form, 'clinic': clinic}
    return render(request, 'hospital/reception/register_patient.html', context)


@login_required(login_url='login')
def view_patient_details(request, patient_id):
    """Reception - View patient details"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id)
    prescriptions = patient.prescriptions.all()
    medical_reports = patient.medical_reports.all()
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'medical_reports': medical_reports,
    }
    return render(request, 'hospital/reception/patient_details.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def patient_checkin(request):
    """Reception - Check-in existing patient"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            form = PatientVisitForm(request.POST)
            if form.is_valid():
                visit = form.save(commit=False)
                visit.patient = patient
                visit.checked_in_by = request.user
                visit.save()
                messages.success(request, f"Patient {patient.patient_name} checked in successfully!")
                return redirect('reception_dashboard')
        except Patient.DoesNotExist:
            messages.error(request, "Patient ID not found!")
    
    patients = Patient.objects.all().order_by('patient_name')
    form = PatientVisitForm()
    
    context = {
        'form': form,
        'patients': patients,
    }
    return render(request, 'hospital/reception/patient_checkin.html', context)


@login_required(login_url='login')
def delete_patient(request, patient_id):
    """Reception/Admin - Delete patient"""
    if request.user.role not in ['receptionist', 'admin']:
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        patient_name = patient.patient_name
        patient.delete()
        messages.success(request, f"Patient {patient_name} deleted successfully!")
        return redirect('reception_dashboard')
    
    context = {'patient': patient}
    return render(request, 'hospital/reception/confirm_delete_patient.html', context)


# ==================== DOCTOR VIEWS ====================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def doctor_dashboard(request, clinic_slug=None):
    """Doctor dashboard - View patients for prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found!")
        return redirect('homepage')
    
    # Resolve clinic: URL slug -> middleware -> user's clinic -> doctor's clinic
    clinic = getattr(request, 'clinic', None)
    if not clinic and clinic_slug:
        try:
            clinic = Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            clinic = None
    if not clinic and getattr(request.user, 'clinic', None):
        clinic = request.user.clinic
    if not clinic and getattr(doctor, 'clinic', None):
        clinic = doctor.clinic
    
    # Get clinic-specific patients
    if clinic:
        patients = Patient.objects.filter(clinic=clinic).order_by('-registration_date')
        prescriptions = Prescription.objects.filter(doctor=doctor, clinic=clinic).order_by('-prescription_date')
    else:
        patients = Patient.objects.all().order_by('-registration_date')
        prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-prescription_date')
    
    pending_prescriptions = prescriptions.filter(status='pending')
    pending_test_results = Test.objects.filter(prescription__doctor=doctor, clinic=clinic, is_completed=False) if clinic else Test.objects.filter(prescription__doctor=doctor, is_completed=False)
    
    # Get today's consultations from PatientVisit
    from django.utils import timezone
    today = timezone.now().date()
    todays_consultations = PatientVisit.objects.filter(doctor=doctor, check_in_date__date=today, clinic=clinic) if clinic else PatientVisit.objects.filter(doctor=doctor, check_in_date__date=today)
    
    context = {
        'doctor': doctor,
        'clinic': clinic,
        'patients': patients,
        'prescriptions': prescriptions,
        'pending_prescriptions': pending_prescriptions,
        'pending_test_results': pending_test_results,
        'todays_consultations': todays_consultations,
        'total_patients': patients.count(),
    }
    return render(request, 'hospital/doctor/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_prescription(request, patient_id):
    """Doctor - Create prescription for patient"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = Doctor.objects.get(user=request.user)
    
    if request.method == 'POST':
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=doctor
        )
        messages.success(request, "Prescription created! Now add tests and medicines.")
        return redirect('add_prescription_details', prescription_id=prescription.id)
    
    context = {'patient': patient}
    return render(request, 'hospital/doctor/create_prescription.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_prescription_details(request, prescription_id):
    """Doctor - Add tests, medicines, and notes to prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = Doctor.objects.get(user=request.user)
    
    if prescription.doctor != doctor:
        return redirect('doctor_dashboard')
    
    tests = prescription.tests.all()
    medicines = prescription.medicines.all()
    doctor_notes = prescription.doctor_notes if hasattr(prescription, 'doctor_notes') else None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_test':
            form = TestForm(request.POST)
            if form.is_valid():
                test = form.save(commit=False)
                test.prescription = prescription
                test.save()
                messages.success(request, "Test added successfully!")
                return redirect('add_prescription_details', prescription_id=prescription.id)
        
        elif action == 'add_medicine':
            form = MedicineForm(request.POST)
            if form.is_valid():
                medicine = form.save(commit=False)
                medicine.prescription = prescription
                medicine.save()
                messages.success(request, "Medicine added successfully!")
                return redirect('add_prescription_details', prescription_id=prescription.id)
        
        elif action == 'save_notes':
            notes_form = DoctorNotesForm(request.POST, instance=doctor_notes)
            if notes_form.is_valid():
                notes = notes_form.save(commit=False)
                notes.prescription = prescription
                notes.save()
                messages.success(request, "Notes saved successfully!")
                return redirect('add_prescription_details', prescription_id=prescription.id)
    
    test_form = TestForm()
    medicine_form = MedicineForm()
    notes_form = DoctorNotesForm(instance=doctor_notes) if doctor_notes else DoctorNotesForm()
    
    context = {
        'prescription': prescription,
        'tests': tests,
        'medicines': medicines,
        'doctor_notes': doctor_notes,
        'test_form': test_form,
        'medicine_form': medicine_form,
        'notes_form': notes_form,
    }
    return render(request, 'hospital/doctor/add_prescription_details.html', context)


@login_required(login_url='login')
def complete_prescription(request, prescription_id):
    """Doctor - Complete prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = Doctor.objects.get(user=request.user)
    
    if prescription.doctor != doctor:
        return redirect('doctor_dashboard')
    
    if request.method == 'POST':
        prescription.status = 'completed'
        prescription.save()
        messages.success(request, "Prescription completed!")
        return redirect('doctor_dashboard')
    
    context = {'prescription': prescription}
    return render(request, 'hospital/doctor/complete_prescription.html', context)


@login_required(login_url='login')
def print_prescription(request, prescription_id):
    """Print prescription as PDF/printable format"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check if user is the doctor who created it or the patient
    if request.user.role == 'doctor':
        doctor = Doctor.objects.get(user=request.user)
        if prescription.doctor != doctor:
            return redirect('doctor_dashboard')
    elif request.user.role == 'patient':
        patient = Patient.objects.get(user=request.user)
        if prescription.patient != patient:
            return redirect('patient_dashboard')
    else:
        return redirect('homepage')
    
    tests = prescription.tests.all()
    medicines = prescription.medicines.all()
    doctor_notes = prescription.doctor_notes if hasattr(prescription, 'doctor_notes') else None
    
    context = {
        'prescription': prescription,
        'tests': tests,
        'medicines': medicines,
        'doctor_notes': doctor_notes,
    }
    return render(request, 'hospital/print_prescription.html', context)


def delete_test(request, test_id):
    """Doctor - Delete test from prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    test = get_object_or_404(Test, id=test_id)
    prescription_id = test.prescription.id
    test.delete()
    messages.success(request, "Test deleted!")
    return redirect('add_prescription_details', prescription_id=prescription_id)


@login_required(login_url='login')
def delete_medicine(request, medicine_id):
    """Doctor - Delete medicine from prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    prescription_id = medicine.prescription.id
    medicine.delete()
    messages.success(request, "Medicine deleted!")
    return redirect('add_prescription_details', prescription_id=prescription_id)


@login_required(login_url='login')
def patient_history(request, patient_id):
    """Doctor - View patient's complete history"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id)
    visits = patient.visits.all()
    prescriptions = patient.prescriptions.all()
    test_reports = patient.test_reports.all()
    medical_reports = patient.medical_reports.all()
    
    context = {
        'patient': patient,
        'visits': visits,
        'prescriptions': prescriptions,
        'test_reports': test_reports,
        'medical_reports': medical_reports,
    }
    return render(request, 'hospital/doctor/patient_history.html', context)


# ==================== PATIENT VIEWS ====================

@login_required(login_url='login')
def patient_dashboard(request, clinic_slug=None):
    """Patient dashboard"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('homepage')
    
    # Resolve clinic: URL slug -> middleware -> user's clinic -> patient's clinic
    clinic = getattr(request, 'clinic', None)
    if not clinic and clinic_slug:
        try:
            clinic = Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            clinic = None
    if not clinic and getattr(request.user, 'clinic', None):
        clinic = request.user.clinic
    if not clinic and getattr(patient, 'clinic', None):
        clinic = patient.clinic
    
    prescriptions = patient.prescriptions.all().order_by('-prescription_date')
    medical_reports = patient.medical_reports.all().order_by('-uploaded_date')
    test_reports = patient.test_reports.all().order_by('-uploaded_date')
    
    # Get pending tests (tests awaiting lab submission)
    pending_tests = Test.objects.filter(prescription__patient=patient, is_completed=False).count()
    
    # Get recent visits
    recent_visits = PatientVisit.objects.filter(patient=patient).order_by('-check_in_date')[:5]
    
    # Get appointments (future visits)
    from django.utils import timezone
    upcoming_visits = PatientVisit.objects.filter(patient=patient, check_in_date__date__gte=timezone.now().date()).order_by('check_in_date')[:3]
    
    context = {
        'patient': patient,
        'clinic': clinic,
        'prescriptions': prescriptions,
        'medical_reports': medical_reports,
        'test_reports': test_reports,
        'pending_tests': pending_tests,
        'recent_visits': recent_visits,
        'upcoming_visits': upcoming_visits,
    }
    return render(request, 'hospital/patient/dashboard.html', context)


@login_required(login_url='login')
def view_prescription(request, prescription_id):
    """Patient - View prescription details"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    prescription = get_object_or_404(Prescription, id=prescription_id)
    patient = Patient.objects.get(user=request.user)
    
    if prescription.patient != patient:
        return redirect('patient_dashboard')
    
    tests = prescription.tests.all()
    medicines = prescription.medicines.all()
    doctor_notes = prescription.doctor_notes if hasattr(prescription, 'doctor_notes') else None
    
    context = {
        'prescription': prescription,
        'tests': tests,
        'medicines': medicines,
        'doctor_notes': doctor_notes,
    }
    return render(request, 'hospital/patient/view_prescription.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def upload_medical_report(request):
    """Patient - Upload medical report"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('homepage')
    
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = patient
            report.save()
            messages.success(request, "Medical report uploaded successfully!")
            return redirect('patient_dashboard')
    else:
        form = MedicalReportForm()
    
    context = {'form': form}
    return render(request, 'hospital/patient/upload_medical_report.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def upload_test_report(request):
    """Patient - Upload test report"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('homepage')
    
    if request.method == 'POST':
        form = TestReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = patient
            report.uploaded_by = request.user
            report.save()
            messages.success(request, "Test report uploaded successfully!")
            return redirect('patient_dashboard')
    else:
        form = TestReportForm()
    
    context = {'form': form}
    return render(request, 'hospital/patient/upload_test_report.html', context)


@login_required(login_url='login')
def view_test_reports(request):
    """Patient - View all test reports"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('homepage')
    
    test_reports = patient.test_reports.all()
    
    context = {
        'test_reports': test_reports,
    }
    return render(request, 'hospital/patient/view_test_reports.html', context)


# ==================== ADMIN VIEWS ====================

@login_required(login_url='login')
@login_required(login_url='login')
def admin_dashboard(request, clinic_slug=None):
    """Admin dashboard"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    # Resolve clinic: URL slug -> middleware -> user's clinic
    clinic = getattr(request, 'clinic', None)
    if not clinic and clinic_slug:
        try:
            clinic = Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            clinic = None
    if not clinic and getattr(request.user, 'clinic', None):
        clinic = request.user.clinic
    
    # Filter all data by clinic
    total_patients = Patient.objects.filter(clinic=clinic).count() if clinic else Patient.objects.count()
    total_doctors = Doctor.objects.filter(clinic=clinic).count() if clinic else Doctor.objects.count()
    total_prescriptions = Prescription.objects.filter(clinic=clinic).count() if clinic else Prescription.objects.count()
    total_users = User.objects.filter(clinic=clinic).count() if clinic else User.objects.count()
    total_receptionists = User.objects.filter(clinic=clinic, role='receptionist').count() if clinic else User.objects.filter(role='receptionist').count()
    
    # Get pending items
    pending_prescriptions = Prescription.objects.filter(status='pending', clinic=clinic).count() if clinic else Prescription.objects.filter(status='pending').count()
    pending_tests = Test.objects.filter(is_completed=False, clinic=clinic).count() if clinic else Test.objects.filter(is_completed=False).count()
    
    # Get today's stats
    from django.utils import timezone
    today = timezone.now().date()
    todays_patients = PatientVisit.objects.filter(check_in_date__date=today, clinic=clinic).count() if clinic else PatientVisit.objects.filter(check_in_date__date=today).count()
    
    # Get recent registrations
    recent_patients = Patient.objects.filter(clinic=clinic).order_by('-registration_date')[:5] if clinic else Patient.objects.order_by('-registration_date')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_prescriptions': total_prescriptions,
        'total_users': total_users,
        'total_receptionists': total_receptionists,
        'pending_prescriptions': pending_prescriptions,
        'pending_tests': pending_tests,
        'todays_patients': todays_patients,
        'recent_patients': recent_patients,
        'clinic': clinic,
    }
    return render(request, 'hospital/admin/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_doctor(request, clinic_slug=None):
    """Admin - Create doctor user and profile"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    if request.method == 'POST':
        user_form = DoctorUserCreationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'doctor'
            user.clinic = clinic
            user.save()
            
            doctor = profile_form.save(commit=False)
            doctor.user = user
            doctor.clinic = clinic
            doctor.save()
            
            messages.success(request, f"Doctor {user.first_name} {user.last_name} created successfully!")
            return redirect('admin_dashboard', clinic_slug=clinic.slug)
    else:
        user_form = DoctorUserCreationForm()
        profile_form = DoctorProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'clinic': clinic,
    }
    return render(request, 'hospital/admin/create_doctor.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_receptionist(request, clinic_slug=None):
    """Admin - Create receptionist user"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    if request.method == 'POST':
        form = ReceptionistUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'receptionist'
            user.clinic = clinic
            user.save()
            messages.success(request, f"Receptionist {user.first_name} {user.last_name} created successfully!")
            return redirect('admin_dashboard', clinic_slug=clinic.slug)
    else:
        form = ReceptionistUserCreationForm()
    
    context = {'form': form, 'clinic': clinic}
    return render(request, 'hospital/admin/create_receptionist.html', context)


@login_required(login_url='login')
def view_all_patients(request, clinic_slug=None):
    """Admin - View all patients"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    patients = Patient.objects.filter(clinic=clinic).order_by('-registration_date')
    context = {'patients': patients, 'clinic': clinic}
    return render(request, 'hospital/admin/view_all_patients.html', context)


@login_required(login_url='login')
def view_all_doctors(request, clinic_slug=None):
    """Admin - View all doctors"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    doctors = Doctor.objects.filter(clinic=clinic)
    context = {'doctors': doctors, 'clinic': clinic}
    return render(request, 'hospital/admin/view_all_doctors.html', context)


@login_required(login_url='login')
def delete_doctor(request, clinic_slug, doctor_id):
    """Admin - Delete doctor"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    doctor = get_object_or_404(Doctor, id=doctor_id, clinic=clinic)
    
    if request.method == 'POST':
        user_name = doctor.user.get_full_name()
        doctor.user.delete()
        messages.success(request, f"Doctor {user_name} deleted successfully!")
        return redirect('view_all_doctors', clinic_slug=clinic.slug)
    
    context = {'doctor': doctor, 'clinic': clinic}
    return render(request, 'hospital/admin/confirm_delete_doctor.html', context)


@login_required(login_url='login')
def delete_receptionist(request, clinic_slug, user_id):
    """Admin - Delete receptionist"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    user = get_object_or_404(User, id=user_id, role='receptionist', clinic=clinic)
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f"Receptionist {user_name} deleted successfully!")
        return redirect('view_all_receptionists', clinic_slug=clinic.slug)
    
    context = {'user': user, 'clinic': clinic}
    return render(request, 'hospital/admin/confirm_delete_receptionist.html', context)


@login_required(login_url='login')
def view_all_receptionists(request, clinic_slug=None):
    """Admin - View all receptionists"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    receptionists = User.objects.filter(role='receptionist', clinic=clinic)
    context = {'receptionists': receptionists, 'clinic': clinic}
    return render(request, 'hospital/admin/view_all_receptionists.html', context)
