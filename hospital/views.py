from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, MedicalReport, Prescription

# Homepage view
def homepage(request):
    return render(request, 'hospital/homepage.html')

# Patient registration view
def register_patient(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'hospital/register_patient.html', {'form': form})

# Patient dashboard view
def patient_dashboard(request):
    return render(request, 'hospital/patient_dashboard.html')

# File upload view
def upload_medical_report(request):
    if request.method == 'POST' and request.FILES['report_file']:
        report = MedicalReport(patient=request.user.patient, report_file=request.FILES['report_file'])
        report.save()
        return redirect('patient_dashboard')
    return render(request, 'hospital/upload_medical_report.html')

# Prescription download view
def download_prescription(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    return render(request, 'hospital/download_prescription.html', {'prescription': prescription})
