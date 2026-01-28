from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Patient, MedicalReport, Prescription, Doctor, Test, Medicine, DoctorNotes, User, PatientVisit, TestReport
from .forms import (PatientRegistrationForm, PrescriptionForm, TestForm, MedicineForm,
                    DoctorNotesForm, MedicalReportForm, DoctorUserCreationForm, 
                    ReceptionistUserCreationForm, DoctorProfileForm, PatientVisitForm, TestReportForm)


# ==================== AUTHENTICATION VIEWS ====================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        if request.user.role == 'patient':
            return redirect('patient_dashboard')
        elif request.user.role == 'doctor':
            return redirect('doctor_dashboard')
        elif request.user.role == 'receptionist':
            return redirect('reception_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            
            if next_url:
                return redirect(next_url)
            
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'receptionist':
                return redirect('reception_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
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
        if request.user.role == 'patient':
            return redirect('patient_dashboard')
        elif request.user.role == 'doctor':
            return redirect('doctor_dashboard')
        elif request.user.role == 'receptionist':
            return redirect('reception_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
    
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
    }
    return render(request, 'hospital/homepage.html', context)


# ==================== RECEPTION VIEWS ====================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def reception_dashboard(request):
    """Reception person dashboard"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    patients = Patient.objects.all().order_by('-registration_date')
    context = {
        'patients': patients,
        'total_patients': patients.count(),
    }
    return render(request, 'hospital/reception/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def register_patient(request):
    """Reception - Register new patient"""
    if request.user.role != 'receptionist':
        return redirect('homepage')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.save()
            
            messages.success(
                request,
                f"Patient {patient.patient_name} registered successfully! "
                f"Patient ID: {patient.patient_id}, Password: {patient.default_password}"
            )
            return redirect('reception_dashboard')
    else:
        form = PatientRegistrationForm()
    
    context = {'form': form}
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
def doctor_dashboard(request):
    """Doctor dashboard - View patients for prescription"""
    if request.user.role != 'doctor':
        return redirect('homepage')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found!")
        return redirect('homepage')
    
    # Get patients that need prescriptions or have pending prescriptions
    patients = Patient.objects.all()
    prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-prescription_date')
    pending_prescriptions = prescriptions.filter(status='pending')
    
    context = {
        'doctor': doctor,
        'patients': patients,
        'prescriptions': prescriptions,
        'pending_prescriptions': pending_prescriptions,
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
def patient_dashboard(request):
    """Patient dashboard"""
    if request.user.role != 'patient':
        return redirect('homepage')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('homepage')
    
    prescriptions = patient.prescriptions.all()
    medical_reports = patient.medical_reports.all()
    test_reports = patient.test_reports.all()
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'medical_reports': medical_reports,
        'test_reports': test_reports,
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
def admin_dashboard(request):
    """Admin dashboard"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_prescriptions = Prescription.objects.count()
    total_users = User.objects.count()
    total_receptionists = User.objects.filter(role='receptionist').count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_prescriptions': total_prescriptions,
        'total_users': total_users,
        'total_receptionists': total_receptionists,
    }
    return render(request, 'hospital/admin/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_doctor(request):
    """Admin - Create doctor user and profile"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    if request.method == 'POST':
        user_form = DoctorUserCreationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'doctor'
            user.save()
            
            doctor = profile_form.save(commit=False)
            doctor.user = user
            doctor.save()
            
            messages.success(request, f"Doctor {user.first_name} {user.last_name} created successfully!")
            return redirect('admin_dashboard')
    else:
        user_form = DoctorUserCreationForm()
        profile_form = DoctorProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'hospital/admin/create_doctor.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_receptionist(request):
    """Admin - Create receptionist user"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    if request.method == 'POST':
        form = ReceptionistUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'receptionist'
            user.save()
            messages.success(request, f"Receptionist {user.first_name} {user.last_name} created successfully!")
            return redirect('admin_dashboard')
    else:
        form = ReceptionistUserCreationForm()
    
    context = {'form': form}
    return render(request, 'hospital/admin/create_receptionist.html', context)


@login_required(login_url='login')
def view_all_patients(request):
    """Admin - View all patients"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    patients = Patient.objects.all().order_by('-registration_date')
    context = {'patients': patients}
    return render(request, 'hospital/admin/view_all_patients.html', context)


@login_required(login_url='login')
def view_all_doctors(request):
    """Admin - View all doctors"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'hospital/admin/view_all_doctors.html', context)


@login_required(login_url='login')
def delete_doctor(request, doctor_id):
    """Admin - Delete doctor"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        user_name = doctor.user.get_full_name()
        doctor.user.delete()
        messages.success(request, f"Doctor {user_name} deleted successfully!")
        return redirect('view_all_doctors')
    
    context = {'doctor': doctor}
    return render(request, 'hospital/admin/confirm_delete_doctor.html', context)


@login_required(login_url='login')
def delete_receptionist(request, user_id):
    """Admin - Delete receptionist"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    user = get_object_or_404(User, id=user_id, role='receptionist')
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f"Receptionist {user_name} deleted successfully!")
        return redirect('view_all_receptionists')
    
    context = {'user': user}
    return render(request, 'hospital/admin/confirm_delete_receptionist.html', context)


@login_required(login_url='login')
def view_all_receptionists(request):
    """Admin - View all receptionists"""
    if request.user.role != 'admin':
        return redirect('homepage')
    
    receptionists = User.objects.filter(role='receptionist')
    context = {'receptionists': receptionists}
    return render(request, 'hospital/admin/view_all_receptionists.html', context)
