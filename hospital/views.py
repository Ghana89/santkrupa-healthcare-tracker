from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.http import JsonResponse
from .models import (Patient, MedicalReport, Prescription, Doctor, Test, Medicine, DoctorNotes, User, 
                    PatientVisit, TestReport, Clinic, MasterMedicine, MasterTest, PatientAdmission, TreatmentLog, Vitals)
from .forms import (PatientRegistrationForm, PrescriptionForm, TestForm, MedicineForm,
                    DoctorNotesForm, MedicalReportForm, DoctorUserCreationForm, 
                    ReceptionistUserCreationForm, DoctorProfileForm, PatientVisitForm, TestReportForm, ClinicRegistrationForm)
from django.utils.crypto import get_random_string

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def receptionist_upload_medical_report(request, clinic_slug, patient_id):
    """Receptionist - Upload medical report for a patient"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic   )
    if request.method == 'POST':
        report_type = request.POST.get('report_type', 'Other')
        description = request.POST.get('description', '')
        if 'report_file' in request.FILES:
            report = MedicalReport(
                clinic=clinic,
                patient=patient,
                report_type=report_type,
                description=description,
                report_file=request.FILES['report_file']
            )
            report.save()
            messages.success(request, f"{report_type} uploaded successfully!")
            return redirect('patient_details', clinic_slug=clinic_slug, patient_id=patient.id)
        else:
            messages.error(request, "Please select a file to upload.")
    context = {
        'patient': patient,
        'clinic': clinic,
        'report_types': [
            ('Lab Report', 'Lab Report'),
            ('X-Ray', 'X-Ray'),
            ('CT Scan', 'CT Scan'),
            ('Ultrasound', 'Ultrasound'),
            ('ECG', 'ECG'),
            ('Blood Test', 'Blood Test'),
            ('COVID Report', 'COVID Report'),
            ('Discharge Summary', 'Discharge Summary'),
            ('Other', 'Other'),
        ]
    }
    return render(request, 'hospital/reception/upload_medical_report.html', context)
    # ...existing code...
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import (Patient, MedicalReport, Prescription, Doctor, Test, Medicine, DoctorNotes, User, 
                    PatientVisit, TestReport, Clinic, MasterMedicine, MasterTest, PatientAdmission, TreatmentLog)
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

        if request.user.role == 'super_admin':
            return redirect('superadmin_dashboard')
        elif request.user.role == 'patient':
            if target_slug:
                return redirect('patient_dashboard', clinic_slug=target_slug)
            return redirect('homepage')
        elif request.user.role == 'doctor':
            if target_slug:
                return redirect('doctor_dashboard', clinic_slug=target_slug)
            return redirect('homepage')
        elif request.user.role == 'receptionist':
            if target_slug:
                return redirect('reception_dashboard', clinic_slug=target_slug)
            return redirect('homepage')
        elif request.user.role == 'admin':
            if target_slug:
                return redirect('admin_dashboard', clinic_slug=target_slug)
            return redirect('homepage')
        else:
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

            if user.role == 'super_admin':
                return redirect('superadmin_dashboard')
            elif user.role == 'patient':
                if target_clinic:
                    return redirect('patient_dashboard', clinic_slug=target_clinic.slug)
                return redirect('homepage')
            elif user.role == 'doctor':
                if target_clinic:
                    return redirect('doctor_dashboard', clinic_slug=target_clinic.slug)
                return redirect('homepage')
            elif user.role == 'receptionist':
                if target_clinic:
                    return redirect('reception_dashboard', clinic_slug=target_clinic.slug)
                return redirect('homepage')
            elif user.role == 'admin':
                if target_clinic:
                    return redirect('admin_dashboard', clinic_slug=target_clinic.slug)
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

        if request.user.role == 'super_admin':
            # Platform owner stays on homepage
            pass
        elif request.user.role == 'patient':
            if target_slug:
                return redirect('patient_dashboard', clinic_slug=target_slug)
            # No clinic association - stay on homepage
        elif request.user.role == 'doctor':
            if target_slug:
                return redirect('doctor_dashboard', clinic_slug=target_slug)
            # No clinic association - stay on homepage
        elif request.user.role == 'receptionist':
            if target_slug:
                return redirect('reception_dashboard', clinic_slug=target_slug)
            # No clinic association - stay on homepage
        elif request.user.role == 'admin':
            if target_slug:
                return redirect('admin_dashboard', clinic_slug=target_slug)
            # No clinic association - stay on homepage
    
    # Get clinic context (for clinic-specific homepage if accessed from clinic URL)
    clinic = getattr(request, 'clinic', None)
    clinics = Clinic.objects.filter(is_active=True).order_by('name')
    
    # Calculate statistics
    if clinic:
        # Clinic-specific statistics
        total_patients = Patient.objects.all_clinics().filter(clinic=clinic).count()
        total_doctors = Doctor.objects.all_clinics().filter(clinic=clinic).count()
    else:
        # Platform-wide statistics (for non-clinic users)
        total_patients = Patient.objects.all_clinics().count()
        total_doctors = Doctor.objects.all_clinics().count()
    
    total_clinics = clinics.count()

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_clinics': total_clinics,
        'clinics': clinics,
        'clinic': clinic,
    }
    return render(request, 'hospital/homepage.html', context)


@login_required(login_url='login')
def superadmin_dashboard(request):
    """Platform superadmin dashboard - Manage all clinics"""
    if request.user.role != 'super_admin':
        return redirect('homepage')
    
    clinics = Clinic.objects.all().order_by('name')
    
    context = {
        'clinics': clinics,
        'total_clinics': clinics.count(),
        'active_clinics': clinics.filter(is_active=True).count(),
        'inactive_clinics': clinics.filter(is_active=False).count(),
    }
    return render(request, 'hospital/superadmin/dashboard.html', context)


@login_required(login_url='login')
def delete_clinic(request, clinic_id):
    """Superadmin - Delete a clinic"""
    if request.user.role != 'super_admin':
        return redirect('homepage')
    
    clinic = get_object_or_404(Clinic, id=clinic_id)
    
    if request.method == 'POST':
        clinic_name = clinic.name
        clinic.delete()
        messages.success(request, f"Clinic '{clinic_name}' has been deleted successfully!")
        return redirect('superadmin_dashboard')
    
    context = {'clinic': clinic}
    return render(request, 'hospital/superadmin/confirm_delete_clinic.html', context)


@login_required(login_url='login')
def superadmin_clinic_patients(request, clinic_id):
    """Superadmin - View all patients in a specific clinic"""
    if request.user.role != 'super_admin':
        return redirect('homepage')
    
    clinic = get_object_or_404(Clinic, id=clinic_id)
    patients = Patient.objects.filter(clinic=clinic).order_by('-registration_date')
    
    context = {
        'clinic': clinic,
        'patients': patients,
        'total_patients': patients.count(),
    }
    return render(request, 'hospital/superadmin/clinic_patients.html', context)


@login_required(login_url='login')
def superadmin_clinic_doctors(request, clinic_id):
    """Superadmin - View all doctors in a specific clinic"""
    if request.user.role != 'super_admin':
        return redirect('homepage')
    
    clinic = get_object_or_404(Clinic, id=clinic_id)
    doctors = Doctor.objects.filter(clinic=clinic).order_by('user__first_name')
    
    context = {
        'clinic': clinic,
        'doctors': doctors,
        'total_doctors': doctors.count(),
    }
    return render(request, 'hospital/superadmin/clinic_doctors.html', context)


@login_required(login_url='login')
def superadmin_clinic_prescriptions(request, clinic_id):
    """Superadmin - View all prescriptions in a specific clinic"""
    if request.user.role != 'super_admin':
        return redirect('homepage')
    
    clinic = get_object_or_404(Clinic, id=clinic_id)
    prescriptions = Prescription.objects.filter(clinic=clinic).order_by('-prescription_date')
    
    # Get filter options
    status_filter = request.GET.get('status', '')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)
    
    context = {
        'clinic': clinic,
        'prescriptions': prescriptions,
        'total_prescriptions': prescriptions.count(),
        'status_choices': Prescription.STATUS_CHOICES if hasattr(Prescription, 'STATUS_CHOICES') else [],
        'selected_status': status_filter,
    }
    return render(request, 'hospital/superadmin/clinic_prescriptions.html', context)


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
def view_patient_details(request, clinic_slug, patient_id):
    """Reception/Admin - View patient details. Allow receptionist, admin, and super_admin."""
    if request.user.role not in ['receptionist', 'admin', 'super_admin']:
        return redirect('homepage')
    
    # Resolve clinic context (URL slug -> middleware -> user's clinic)
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)

    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic )
    prescriptions = patient.prescriptions.all()
    medical_reports = patient.medical_reports.all()
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'medical_reports': medical_reports,
        'clinic': clinic,
    }
    return render(request, 'hospital/reception/patient_details.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def patient_checkin(request, clinic_slug=None):
    """Reception - Check-in existing patient"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    # Resolve clinic context
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            form = PatientVisitForm(request.POST)
            if form.is_valid():
                visit = form.save(commit=False)
                visit.patient = patient
                visit.checked_in_by = request.user
                visit.clinic = clinic
                visit.save()
                messages.success(request, f"Patient {patient.patient_name} checked in successfully!")
                if clinic_slug:
                    return redirect('reception_dashboard', clinic_slug=clinic_slug)
                return redirect('reception_dashboard')
        except Patient.DoesNotExist:
            messages.error(request, "Patient ID not found!")
    
    patients = Patient.objects.all().order_by('patient_name')
    form = PatientVisitForm()
    
    context = {
        'form': form,
        'patients': patients,
        'clinic': clinic,
    }
    return render(request, 'hospital/reception/patient_checkin.html', context)


@login_required(login_url='login')
def patient_search(request, clinic_slug=None):
    """AJAX endpoint: search patients by name or patient_id for autocomplete."""
    if request.user.role != 'receptionist':
        return JsonResponse({'error': 'unauthorized'}, status=403)

    q = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 15))

    # Resolve clinic context
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)

    if not q:
        return JsonResponse({'results': []})

    # Search by name or patient_id (case-insensitive partial match)
    qs = Patient.objects.all_clinics() if hasattr(Patient.objects, 'all_clinics') else Patient.objects.all()
    if clinic:
        qs = qs.filter(clinic=clinic)

    from django.db.models import Q
    matches = qs.filter(Q(patient_name__icontains=q) | Q(patient_id__icontains=q)).order_by('patient_name')[:limit]

    results = []
    for p in matches:
        results.append({
            'id': p.id,
            'patient_id': p.patient_id,
            'patient_name': p.patient_name,
        })

    return JsonResponse({'results': results})


@login_required(login_url='login')
def checkin_dashboard(request, clinic_slug=None):
    """Aggregated check-in dashboard supporting day/month/year granularity.

    Accessible to roles: super_admin, admin, receptionist, doctor.
    If clinic_slug provided, data is restricted to that clinic; superadmins can view across clinics.
    """
    if request.user.role not in ['super_admin', 'admin']:
        return redirect('homepage')

    # Resolve clinic context
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)

    # Determine granularity
    gran = request.GET.get('granularity', 'day')  # 'day' | 'month' | 'year'
    from django.db.models.functions import TruncDay, TruncMonth, TruncYear
    from django.db.models import Count

    qs = PatientVisit.objects.all_clinics() if hasattr(PatientVisit.objects, 'all_clinics') else PatientVisit.objects.all()
    if clinic:
        qs = qs.filter(clinic=clinic)

    # Optional date filters
    period = request.GET.get('period', '')  # e.g., 'today', 'this_month', 'this_year'
    from django.utils import timezone
    now = timezone.now()
    if period == 'today':
        qs = qs.filter(check_in_date__date=now.date())
    elif period == 'this_month':
        qs = qs.filter(check_in_date__year=now.year, check_in_date__month=now.month)
    elif period == 'this_year':
        qs = qs.filter(check_in_date__year=now.year)

    if gran == 'month':
        annotated = qs.annotate(period=TruncMonth('check_in_date')).values('period').annotate(count=Count('id')).order_by('period')
    elif gran == 'year':
        annotated = qs.annotate(period=TruncYear('check_in_date')).values('period').annotate(count=Count('id')).order_by('period')
    else:
        annotated = qs.annotate(period=TruncDay('check_in_date')).values('period').annotate(count=Count('id')).order_by('period')

    # Prepare results for template

    results = [{'period': a['period'], 'count': a['count']} for a in annotated]

    # Tabular visits for admin view (Date, Patient ID, Doctor Name, Patient Name, Prescription)
    visits_qs = qs.select_related('patient', 'checked_in_by').order_by('-check_in_date')
    tabular_visits = []
    from .models import Prescription
    for v in visits_qs[:500]:
        # find prescription(s) for this patient on the same day (if any)
        pres = Prescription.objects.filter(patient=v.patient, prescription_date__date=v.check_in_date.date()).order_by('-prescription_date').first()
        if pres and pres.doctor:
            doctor_name = f"Dr. {pres.doctor.user.first_name} {pres.doctor.user.last_name}".strip()
            prescription_link = pres.id
        else:
            doctor_name = ''
            prescription_link = None

        tabular_visits.append({
            'check_in_date': v.check_in_date,
            'patient_id': v.patient.patient_id,
            'patient_name': v.patient.patient_name,
            'patient_pk': v.patient.id,
            'doctor_name': doctor_name,
            'prescription_id': prescription_link,
            'visit_id': v.id,
        })

    # Recent visits list (kept for backward compatibility)
    recent_visits = visits_qs[:50]

    context = {
        'clinic': clinic,
        'granularity': gran,
        'period': period,
        'results': results,
        'recent_visits': recent_visits,
        'tabular_visits': tabular_visits,
        'total_visits': qs.count(),
    }
    return render(request, 'hospital/reception/checkin_dashboard.html', context)


@login_required(login_url='login')
def delete_patient(request, patient_id, clinic_slug=None):
    """Reception/Admin - Delete patient"""
    if request.user.role not in ['receptionist', 'admin']:
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        patient_name = patient.patient_name
        patient.delete()
        messages.success(request, f"Patient {patient_name} deleted successfully!")
        if clinic_slug:
            return redirect('reception_dashboard', clinic_slug=clinic_slug)
        return redirect('reception_dashboard')
    
    context = {'patient': patient}
    # include clinic context for template links
    context['clinic'] = get_clinic_from_slug_or_middleware(clinic_slug, request)
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
    
    # Search filter for patients
    search_query = request.GET.get('search', '').strip()
    if search_query:
        patients = patients.filter(patient_name__icontains=search_query)
    
    pending_prescriptions = prescriptions.filter(status='pending')
    pending_test_results = Test.objects.filter(prescription__doctor=doctor, clinic=clinic, is_completed=False) if clinic else Test.objects.filter(prescription__doctor=doctor, is_completed=False)
    
    # Get today's consultations from PatientVisit (by clinic — PatientVisit has no doctor FK)
    from django.utils import timezone
    today = timezone.now().date()
    print(f"Doctor Dashboard: Fetching today's consultations for doctor {doctor} in clinic {clinic} on {today}")
    if clinic:
        todays_consultations = PatientVisit.objects.filter(
            check_in_date__date=today,
            clinic=clinic,
            status='checked_in'
        )
    else:
        todays_consultations = PatientVisit.objects.filter(
            check_in_date__date=today,
            status='checked_in'
        )
    print(f"Doctor Dashboard: Found {todays_consultations.count()} check-ins for today before filtering by doctor")
    # Search filter for today's check-ins
    checkin_search = request.GET.get('checkin_search', '').strip()
    if checkin_search:
        todays_consultations = todays_consultations.filter(patient__patient_name__icontains=checkin_search)
    
    # Get patients who already have prescriptions (hide from list)
    patients_with_prescriptions = set(Prescription.objects.filter(doctor=doctor, clinic=clinic, prescription_date=today).values_list('patient_id', flat=True))
    print(f"Doctor Dashboard: Patients with prescriptions today: {patients_with_prescriptions}")
    available_patients = patients.exclude(id__in=patients_with_prescriptions)
    
    # Get today's check-ins without prescriptions
    todays_checkins_without_prescription = todays_consultations.exclude(patient_id__in=patients_with_prescriptions)
    
    context = {
        'doctor': doctor,
        'clinic': clinic,
        'patients': available_patients,
        'prescriptions': prescriptions,
        'pending_prescriptions': pending_prescriptions,
        'pending_test_results': pending_test_results,
        'todays_consultations': todays_checkins_without_prescription,
        'total_patients': patients.count(),
        'search_query': search_query,
        'checkin_search': checkin_search,
    }
    return render(request, 'hospital/doctor/dashboard.html', context)


@login_required(login_url='login')
def doctor_prescription_tracking(request, clinic_slug=None):
    """Doctor - View and track all prescriptions created"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found!")
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    if clinic:
        prescriptions = Prescription.objects.filter(doctor=doctor, clinic=clinic).order_by('-prescription_date')
    else:
        prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-prescription_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter in ['pending', 'completed', 'cancelled']:
        prescriptions = prescriptions.filter(status=status_filter)
    
    # Search by patient name
    search_query = request.GET.get('search', '').strip()
    if search_query:
        prescriptions = prescriptions.filter(patient__patient_name__icontains=search_query)
    
    context = {
        'doctor': doctor,
        'clinic': clinic,
        'prescriptions': prescriptions,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'hospital/doctor/prescription_tracking.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_prescription(request, patient_id, clinic_slug=None):
    """Doctor - Create prescription for patient (clinic-aware)"""
    if request.user.role != 'doctor':
        return redirect('homepage')

    # Resolve clinic context
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)

    patient = get_object_or_404(Patient, id=patient_id)
    doctor = Doctor.objects.get(user=request.user)

    if request.method == 'POST':
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            clinic=clinic
        )
        messages.success(request, "Prescription created! Now add tests and medicines.")
        if clinic_slug:
            return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription.id)
        return redirect('add_prescription_details', prescription_id=prescription.id)

    context = {'patient': patient, 'clinic': clinic}
    return render(request, 'hospital/doctor/create_prescription.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_prescription_details(request, prescription_id, clinic_slug=None):
    """Doctor - Add tests, medicines, and notes to prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    # Resolve clinic context for clinic-aware URL reversing
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)

    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = Doctor.objects.get(user=request.user)
    vitals = getattr(prescription, 'vitals', None)

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
            if clinic_slug:
                return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription.id)
            return redirect('add_prescription_details', prescription_id=prescription.id)
        
        elif action == 'save_vitals':
            bp = request.POST.get('bp')
            pulse = request.POST.get('pulse')
            temp = request.POST.get('temp')
            spo2 = request.POST.get('spo2')

            vitals_obj, created = Vitals.objects.get_or_create(
                prescription=prescription,
                defaults={
                    'clinic': prescription.clinic
                }
            )

            vitals_obj.bp = bp
            vitals_obj.pulse = pulse
            vitals_obj.temp = temp
            vitals_obj.spo2 = spo2
            vitals_obj.save()

            messages.success(request, "Vitals saved successfully!")

            # 🔥 IMPORTANT: redirect after POST
            if clinic_slug:
                return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription.id)
            return redirect('add_prescription_details', prescription_id=prescription.id)
            
        elif action == 'add_medicine':
            form = MedicineForm(request.POST)
            if form.is_valid():
                medicine = form.save(commit=False)
                medicine.prescription = prescription
                medicine.save()
                messages.success(request, "Medicine added successfully!")
            if clinic_slug:
                return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription.id)
            return redirect('add_prescription_details', prescription_id=prescription.id)
    
        elif action == 'save_notes':
            notes_form = DoctorNotesForm(request.POST, instance=doctor_notes)
            if notes_form.is_valid():
                notes = notes_form.save(commit=False)
                notes.prescription = prescription
                notes.save()
                messages.success(request, "Notes saved successfully!")
            if clinic_slug:
                return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription.id)
            return redirect('add_prescription_details', prescription_id=prescription.id)

    test_form = TestForm()
    medicine_form = MedicineForm()
    notes_form = DoctorNotesForm(instance=doctor_notes) if doctor_notes else DoctorNotesForm()
    vitals = Vitals.objects.filter(prescription=prescription).first()
    
    context = {
        'prescription': prescription,
        'tests': tests,
        'medicines': medicines,
        'doctor_notes': doctor_notes,
        'clinic': clinic,
        'test_form': test_form,
        'medicine_form': medicine_form,
        'notes_form': notes_form,
        'vitals': vitals,
    }
    return render(request, 'hospital/doctor/add_prescription_details.html', context)


@login_required(login_url='login')
def complete_prescription(request, prescription_id, clinic_slug=None):
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
        from django.utils import timezone
        today = timezone.now().date()
        patient_visit = PatientVisit.objects.filter(
            patient=prescription.patient,
            clinic=prescription.clinic,
            check_in_date__date=today,
            status='checked_in'
        ).first()

        if patient_visit:
            patient_visit.status = 'completed'
            patient_visit.save()
        messages.success(request, "Prescription completed!")
        if clinic_slug:
            return redirect('doctor_dashboard', clinic_slug=clinic_slug)
        return redirect('doctor_dashboard')
    
    context = {'prescription': prescription}
    return render(request, 'hospital/doctor/complete_prescription.html', context)


@login_required(login_url='login')
def print_prescription(request, prescription_id, clinic_slug=None):
    """Print prescription as PDF/printable format"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check if user is the doctor who created it or the patient
    if request.user.role == 'doctor':
        doctor = Doctor.objects.get(user=request.user)
        if prescription.doctor != doctor:
            if clinic_slug:
                return redirect('doctor_dashboard', clinic_slug=clinic_slug)
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
    vitals = getattr(prescription, 'vitals', None)

    context = {
        'prescription': prescription,
        'tests': tests,
        'medicines': medicines,
        'doctor_notes': doctor_notes,
        'vitals': vitals,
    }
    return render(request, 'hospital/print_prescription.html', context)


def delete_test(request, test_id, clinic_slug=None):
    """Doctor - Delete test from prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    test = get_object_or_404(Test, id=test_id)
    prescription_id = test.prescription.id
    test.delete()
    messages.success(request, "Test deleted!")
    if clinic_slug:
        return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription_id)
    return redirect('add_prescription_details', prescription_id=prescription_id)


@login_required(login_url='login')
def delete_medicine(request, medicine_id, clinic_slug=None):
    """Doctor - Delete medicine from prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    prescription_id = medicine.prescription.id
    medicine.delete()
    messages.success(request, "Medicine deleted!")
    if clinic_slug:
        return redirect('add_prescription_details', clinic_slug=clinic_slug, prescription_id=prescription_id)
    return redirect('add_prescription_details', prescription_id=prescription_id)


@login_required(login_url='login')
def patient_history(request, patient_id, clinic_slug=None):
    """Doctor - View patient's complete history"""
    # Allow doctors, clinic admins, and superadmins to view patient history
    if request.user.role not in ['doctor', 'admin', 'super_admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    patient = get_object_or_404(Patient, id=patient_id)
    visits = patient.visits.all()
    prescriptions = patient.prescriptions.all()
    test_reports = patient.test_reports.all()
    medical_reports = patient.medical_reports.all()
    
    context = {
        'clinic': clinic,
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
    # Allow patients to view their own prescriptions and allow admin/doctor/super_admin to view any
    if request.user.role == 'patient':
        prescription = get_object_or_404(Prescription, id=prescription_id)
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return redirect('homepage')

        if prescription.patient != patient:
            return redirect('patient_dashboard')
    else:
        if request.user.role not in ['admin', 'super_admin', 'doctor']:
            return redirect('homepage')
        prescription = get_object_or_404(Prescription, id=prescription_id)
    
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


# ==================== MASTER DATA MANAGEMENT VIEWS ====================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def manage_master_medicines(request, clinic_slug=None):
    """Admin/Doctor - Register and manage master medicines"""
    if request.user.role not in ['admin', 'doctor', 'super_admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    if not clinic:
        messages.error(request, "Clinic not found!")
        return redirect('homepage')
    
    if request.method == 'POST':
        from .models import MasterMedicine
        medicine_name = request.POST.get('medicine_name', '').strip()
        dosage_options = request.POST.get('dosage_options', '').strip()
        frequency_options = request.POST.get('frequency_options', '').strip()
        default_frequency = request.POST.get('default_frequency', '').strip()
        default_duration = request.POST.get('default_duration', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not medicine_name or not dosage_options or not frequency_options:
            messages.error(request, "Medicine name, dosage options, and frequency options are required!")
        else:
            try:
                existing = MasterMedicine.objects.filter(clinic=clinic, medicine_name__iexact=medicine_name).exists()
                if existing:
                    messages.warning(request, f"Medicine '{medicine_name}' already exists!")
                else:
                    MasterMedicine.objects.create(
                        clinic=clinic,
                        medicine_name=medicine_name,
                        dosage_options=dosage_options,
                        frequency_options=frequency_options,
                        default_frequency=default_frequency,
                        default_duration=default_duration,
                        category=category,
                        description=description,
                        is_active=True
                    )
                    messages.success(request, f"Medicine '{medicine_name}' registered successfully!")
            except Exception as e:
                messages.error(request, f"Error registering medicine: {str(e)}")
        
        return redirect('manage_master_medicines', clinic_slug=clinic.slug)
    
    from .models import MasterMedicine
    medicines = MasterMedicine.objects.filter(clinic=clinic, is_active=True).order_by('medicine_name')
    
    context = {
        'clinic': clinic,
        'medicines': medicines,
    }
    return render(request, 'hospital/admin/manage_master_medicines.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_master_medicine(request, medicine_id, clinic_slug=None):
    """Delete a master medicine"""
    if request.user.role not in ['admin', 'super_admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    from .models import MasterMedicine
    medicine = get_object_or_404(MasterMedicine, id=medicine_id, clinic=clinic)
    medicine_name = medicine.medicine_name
    medicine.delete()
    messages.success(request, f"Medicine '{medicine_name}' deleted successfully!")
    
    return redirect('manage_master_medicines', clinic_slug=clinic.slug)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def manage_master_tests(request, clinic_slug=None):
    """Admin/Doctor - Register and manage master tests"""
    if request.user.role not in ['admin', 'doctor', 'super_admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    if not clinic:
        messages.error(request, "Clinic not found!")
        return redirect('homepage')
    
    if request.method == 'POST':
        from .models import MasterTest
        test_name = request.POST.get('test_name', '').strip()
        test_type = request.POST.get('test_type', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not test_name or not test_type:
            messages.error(request, "Test name and test type are required!")
        else:
            try:
                existing = MasterTest.objects.filter(clinic=clinic, test_name__iexact=test_name).exists()
                if existing:
                    messages.warning(request, f"Test '{test_name}' already exists!")
                else:
                    MasterTest.objects.create(
                        clinic=clinic,
                        test_name=test_name,
                        test_type=test_type,
                        category=category,
                        description=description,
                        is_active=True
                    )
                    messages.success(request, f"Test '{test_name}' registered successfully!")
            except Exception as e:
                messages.error(request, f"Error registering test: {str(e)}")
        
        return redirect('manage_master_tests', clinic_slug=clinic.slug)
    
    from .models import MasterTest
    tests = MasterTest.objects.filter(clinic=clinic, is_active=True).order_by('test_type', 'test_name')
    test_types = MasterTest.TEST_TYPES
    
    context = {
        'clinic': clinic,
        'tests': tests,
        'test_types': test_types,
    }
    return render(request, 'hospital/admin/manage_master_tests.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_master_test(request, test_id, clinic_slug=None):
    """Delete a master test"""
    if request.user.role not in ['admin', 'super_admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    from .models import MasterTest
    test = get_object_or_404(MasterTest, id=test_id, clinic=clinic)
    test_name = test.test_name
    test.delete()
    messages.success(request, f"Test '{test_name}' deleted successfully!")
    
    return redirect('manage_master_tests', clinic_slug=clinic.slug)


@login_required(login_url='login')
@require_http_methods(["GET"])
def api_master_medicines(request, clinic_slug=None):
    """AJAX API - Get master medicines by category or search"""
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    from .models import MasterMedicine
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    medicines = MasterMedicine.objects.filter(clinic=clinic, is_active=True)
    
    if q:
        medicines = medicines.filter(medicine_name__icontains=q)
    
    if category:
        medicines = medicines.filter(category=category)
    
    data = [
        {
            'id': m.id,
            'medicine_name': m.medicine_name,
            'category': m.category,
            'dosage_options': m.dosage_options,
            'frequency_options': m.frequency_options,
            'default_frequency': m.default_frequency,
            'default_duration': m.default_duration,
        }
        for m in medicines[:20]
    ]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@require_http_methods(["GET"])
def api_master_tests(request, clinic_slug=None):
    """AJAX API - Get master tests by type or search"""
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        clinic = request.user.clinic
    
    from .models import MasterTest
    q = request.GET.get('q', '').strip()
    test_type = request.GET.get('test_type', '').strip()
    
    tests = MasterTest.objects.filter(clinic=clinic, is_active=True)
    
    if q:
        tests = tests.filter(test_name__icontains=q)
    
    if test_type:
        tests = tests.filter(test_type=test_type)
    
    data = [
        {
            'id': t.id,
            'test_name': t.test_name,
            'test_type': t.test_type,
            'category': t.category,
        }
        for t in tests[:20]
    ]
    return JsonResponse(data, safe=False)


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
    total_patients = Patient.objects.all_clinics().filter(clinic=clinic).count() if clinic else Patient.objects.all_clinics().count()
    total_doctors = Doctor.objects.all_clinics().filter(clinic=clinic).count() if clinic else Doctor.objects.all_clinics().count()
    total_prescriptions = Prescription.objects.all_clinics().filter(clinic=clinic).count() if clinic else Prescription.objects.all_clinics().count()
    total_users = User.objects.filter(clinic=clinic).count() if clinic else User.objects.count()
    total_receptionists = User.objects.filter(clinic=clinic, role='receptionist').count() if clinic else User.objects.filter(role='receptionist').count()
    
    # Get pending items
    pending_prescriptions = Prescription.objects.all_clinics().filter(status='pending', clinic=clinic).count() if clinic else Prescription.objects.all_clinics().filter(status='pending').count()
    pending_tests = Test.objects.all_clinics().filter(is_completed=False, clinic=clinic).count() if clinic else Test.objects.all_clinics().filter(is_completed=False).count()
    
    # Get today's stats
    from django.utils import timezone
    today = timezone.now().date()
    todays_patients = PatientVisit.objects.all_clinics().filter(check_in_date__date=today, clinic=clinic).count() if clinic else PatientVisit.objects.all_clinics().filter(check_in_date__date=today).count()
    
    # Get recent registrations
    recent_patients = Patient.objects.all_clinics().filter(clinic=clinic).order_by('-registration_date')[:5] if clinic else Patient.objects.all_clinics().order_by('-registration_date')[:5]
    
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
    
    # Resolve clinic: URL slug -> middleware -> user's clinic
    clinic = getattr(request, 'clinic', None)
    if not clinic and clinic_slug:
        try:
            clinic = Clinic.objects.get(slug=clinic_slug)
        except Clinic.DoesNotExist:
            clinic = None
    if not clinic and getattr(request.user, 'clinic', None):
        clinic = request.user.clinic
    
    if not clinic:
        return redirect('homepage')
    
    if request.method == 'POST':
        user_form = DoctorUserCreationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Create user first
                user = user_form.save(commit=False)
                user.role = 'doctor'
                user.clinic = clinic
                user.save()
                
                # Create doctor profile manually with form data
                doctor = Doctor(
                    user=user,
                    clinic=clinic,
                    specialization=profile_form.cleaned_data['specialization'],
                    license_number=profile_form.cleaned_data['license_number']
                )
                doctor.save()
                
                messages.success(request, f"Doctor {user.first_name} {user.last_name} created successfully!")
                return redirect('admin_dashboard', clinic_slug=clinic.slug)
            except Exception as e:
                messages.error(request, f"Error creating doctor: {str(e)}")
        else:
            # Log form errors for debugging
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    messages.error(request, f"User Form - {field}: {', '.join(errors)}")
            if not profile_form.is_valid():
                for field, errors in profile_form.errors.items():
                    messages.error(request, f"Profile Form - {field}: {', '.join(errors)}")
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
    
    patients = Patient.objects.all_clinics().filter(clinic=clinic).order_by('-registration_date')
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
    
    doctors = Doctor.objects.all_clinics().filter(clinic=clinic)
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


# ============================================================================
# ADMISSION & HOSPITALIZATION VIEWS - Doctor
# ============================================================================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def admit_patient(request, patient_id, clinic_slug=None):
    """Doctor - Admit patient to hospital"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
    doctor = get_object_or_404(Doctor, user=request.user, clinic=clinic)
    
    if request.method == 'POST':
        admission = PatientAdmission(
            clinic=clinic,
            patient=patient,
            doctor=doctor,
            admission_type=request.POST.get('admission_type', 'general'),
            bed_number=request.POST.get('bed_number', ''),
            room_number=request.POST.get('room_number', ''),
            reason_for_admission=request.POST.get('reason_for_admission', ''),
            medical_history=request.POST.get('medical_history', ''),
            allergies=request.POST.get('allergies', ''),
        )
        admission.save()
        messages.success(request, f"Patient {patient.patient_name} admitted successfully!")
        return redirect('admission_details', admission_id=admission.id, clinic_slug=clinic_slug)
    
    context = {
        'patient': patient,
        'clinic': clinic,
        'admission_types': PatientAdmission.ADMISSION_TYPES,
    }
    return render(request, 'hospital/doctor/admit_patient.html', context)


@login_required(login_url='login')
def admission_details(request, admission_id, clinic_slug=None):
    """Doctor - View admission details and add treatments"""
    if request.user.role not in ['doctor', 'admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    admission = get_object_or_404(PatientAdmission, id=admission_id, clinic=clinic)
    treatments = admission.treatment_logs.all().order_by('-administered_date')
    medical_reports = admission.patient.medical_reports.filter(clinic=clinic).order_by('-uploaded_at')
    
    context = {
        'admission': admission,
        'treatments': treatments,
        'medical_reports': medical_reports,
        'clinic': clinic,
        'discharge_statuses': PatientAdmission.DISCHARGE_STATUS,
    }
    return render(request, 'hospital/doctor/admission_details.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_treatment(request, admission_id, clinic_slug=None):
    """Doctor - Add treatment/injection/saline to admission"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    admission = get_object_or_404(PatientAdmission, id=admission_id, clinic=clinic)
    doctor = get_object_or_404(Doctor, user=request.user, clinic=clinic)
    
    if request.method == 'POST':
        from django.utils import timezone
        treatment_type = request.POST.get('treatment_type')
        
        treatment = TreatmentLog(
            clinic=clinic,
            admission=admission,
            administered_by=request.user,
            treatment_type=treatment_type,
            treatment_name=request.POST.get('treatment_name', ''),
            description=request.POST.get('description', ''),
            dosage=request.POST.get('dosage', ''),
            frequency=request.POST.get('frequency', ''),
            route=request.POST.get('route', ''),
            saline_type=request.POST.get('saline_type', ''),
            quantity=request.POST.get('quantity', ''),
            oxygen_flow_rate=request.POST.get('oxygen_flow_rate', ''),
            oxygen_type=request.POST.get('oxygen_type', ''),
            duration=request.POST.get('duration', ''),
            notes=request.POST.get('notes', ''),
            administered_date=timezone.now(),
        )
        treatment.save()
        messages.success(request, "Treatment recorded successfully!")
        return redirect('admission_details', admission_id=admission_id, clinic_slug=clinic_slug)
    
    context = {
        'admission': admission,
        'clinic': clinic,
        'treatment_types': TreatmentLog.TREATMENT_TYPES,
        'medicines': clinic.master_medicines.filter(is_active=True),
    }
    return render(request, 'hospital/doctor/add_treatment.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def update_admission_status(request, admission_id, clinic_slug=None):
    """Doctor - Update admission status"""
    if request.user.role not in ['doctor', 'admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    admission = get_object_or_404(PatientAdmission, id=admission_id, clinic=clinic)
    
    new_status = request.POST.get('status')
    if new_status in dict(PatientAdmission.DISCHARGE_STATUS):
        admission.status = new_status
        
        if new_status == 'discharged':
            from django.utils import timezone
            admission.discharge_date = timezone.now()
            admission.discharge_notes = request.POST.get('discharge_notes', '')
            admission.follow_up_date = request.POST.get('follow_up_date') or None
            admission.follow_up_instructions = request.POST.get('follow_up_instructions', '')
            messages.success(request, f"Patient {admission.patient.patient_name} discharged successfully!")
        
        admission.save()
        messages.success(request, f"Admission status updated to {new_status}!")
    
    return redirect('admission_details', admission_id=admission_id, clinic_slug=clinic_slug)


@login_required(login_url='login')
def patient_admissions(request, patient_id, clinic_slug=None):
    """Doctor - View all admissions for a patient"""
    if request.user.role not in ['doctor', 'admin', 'receptionist']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
    admissions = patient.admissions.all().order_by('-admission_date')
    
    context = {
        'patient': patient,
        'admissions': admissions,
        'clinic': clinic,
    }
    return render(request, 'hospital/doctor/patient_admissions.html', context)


@login_required(login_url='login')
def admissions_dashboard(request, clinic_slug=None):
    """Doctor/Admin - View all current admissions in clinic"""
    if request.user.role not in ['doctor', 'admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    # Current admissions (not discharged)
    current_admissions = clinic.patient_admissions.exclude(status='discharged').order_by('-admission_date')
    discharged_admissions = clinic.patient_admissions.filter(status='discharged').order_by('-discharge_date')[:10]
    
    # Statistics
    total_admitted = current_admissions.count()
    icu_patients = current_admissions.filter(admission_type='icu').count()
    general_ward = current_admissions.filter(admission_type='general').count()
    emergency = current_admissions.filter(admission_type='emergency').count()
    
    search_query = request.GET.get('search', '')
    if search_query:
        current_admissions = current_admissions.filter(
            patient__patient_name__icontains=search_query
        ) | current_admissions.filter(
            patient__patient_id__icontains=search_query
        )
    
    context = {
        'current_admissions': current_admissions,
        'discharged_admissions': discharged_admissions,
        'total_admitted': total_admitted,
        'icu_patients': icu_patients,
        'general_ward': general_ward,
        'emergency': emergency,
        'search_query': search_query,
        'clinic': clinic,
    }
    return render(request, 'hospital/doctor/admissions_dashboard.html', context)


# ============================================================================
# ADMISSION RECOMMENDATION VIEWS - Doctor
# ============================================================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def recommend_admission(request, prescription_id, clinic_slug=None):
    """Doctor - Recommend patient admission from prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    prescription = get_object_or_404(Prescription, id=prescription_id, clinic=clinic)
    doctor = get_object_or_404(Doctor, user=request.user, clinic=clinic)
    
    if prescription.doctor != doctor:
        return redirect('homepage')
    
    # Set admission recommendation
    prescription.admission_recommended = True
    prescription.admission_reason = request.POST.get('admission_reason', '')
    prescription.save()
    
    messages.success(request, "Admission recommended for this patient!")
    return redirect('add_prescription_details', prescription_id=prescription_id, clinic_slug=clinic_slug)


@login_required(login_url='login')
def admission_recommendations(request, clinic_slug=None):
    """Doctor - View all admission recommendations"""
    if request.user.role not in ['doctor', 'admin']:
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    # Get all prescriptions with admission recommended
    recommendations = clinic.prescriptions.filter(admission_recommended=True).select_related(
        'patient', 'doctor'
    ).order_by('-prescription_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'pending':
        # Patients recommended but not yet admitted
        patient_ids = [p.patient_id for p in recommendations]
        admitted_patient_ids = PatientAdmission.objects.filter(
            clinic=clinic,
            status__in=['admitted', 'in_treatment', 'improving', 'stable', 'ready_for_discharge']
        ).values_list('patient_id', flat=True)
        recommendations = recommendations.filter(
            patient_id__in=[p_id for p_id in patient_ids if p_id not in admitted_patient_ids]
        )
    elif status_filter == 'admitted':
        # Patients recommended and already admitted
        admitted_patient_ids = PatientAdmission.objects.filter(
            clinic=clinic,
            status__in=['admitted', 'in_treatment', 'improving', 'stable', 'ready_for_discharge']
        ).values_list('patient_id', flat=True)
        recommendations = recommendations.filter(patient_id__in=admitted_patient_ids)
    
    # Add admission status to each recommendation
    admitted_patient_ids_dict = {}
    for admission in PatientAdmission.objects.filter(
        clinic=clinic,
        status__in=['admitted', 'in_treatment', 'improving', 'stable', 'ready_for_discharge']
    ).values_list('patient_id', 'id'):
        admitted_patient_ids_dict[admission[0]] = admission[1]
    
    recommendations_with_status = []
    for rec in recommendations:
        rec.is_admitted = rec.patient_id in admitted_patient_ids_dict
        rec.current_admission_id = admitted_patient_ids_dict.get(rec.patient_id)
        recommendations_with_status.append(rec)
    
    context = {
        'recommendations': recommendations_with_status,
        'clinic': clinic,
        'status_filter': status_filter,
    }
    return render(request, 'hospital/doctor/admission_recommendations.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def upload_admission_report(request, admission_id, clinic_slug=None):
    """Doctor - Upload medical report for patient admission"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    clinic = get_clinic_from_slug_or_middleware(clinic_slug, request)
    if not clinic:
        return redirect('homepage')
    
    admission = get_object_or_404(PatientAdmission, id=admission_id, clinic=clinic)
    
    if request.method == 'POST':
        from django.core.files.storage import default_storage
        
        report_type = request.POST.get('report_type', 'Other')
        description = request.POST.get('description', '')
        
        if 'report_file' in request.FILES:
            report = MedicalReport(
                clinic=clinic,
                patient=admission.patient,
                report_type=report_type,
                description=description,
                report_file=request.FILES['report_file']
            )
            report.save()
            messages.success(request, f"{report_type} uploaded successfully!")
            return redirect('admission_details', admission_id=admission_id, clinic_slug=clinic_slug)
        else:
            messages.error(request, "Please select a file to upload.")
    
    context = {
        'admission': admission,
        'clinic': clinic,
        'report_types': [
            ('Lab Report', 'Lab Report'),
            ('X-Ray', 'X-Ray'),
            ('CT Scan', 'CT Scan'),
            ('Ultrasound', 'Ultrasound'),
            ('ECG', 'ECG'),
            ('Blood Test', 'Blood Test'),
            ('COVID Report', 'COVID Report'),
            ('Discharge Summary', 'Discharge Summary'),
            ('Other', 'Other'),
        ]
    }
    return render(request, 'hospital/doctor/upload_admission_report.html', context)
