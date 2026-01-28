from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, Prescription, Test, Medicine, DoctorNotes, MedicalReport, Doctor, User, PatientVisit, TestReport


# Reception - Patient Registration Form
class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['patient_name', 'age', 'address', 'phone_number']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full address',
                'rows': 3
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter mobile number'
            }),
        }


# Doctor - Prescription Form
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


# Doctor - Add Test Form
class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['test_type', 'test_name', 'description', 'test_date']
        widgets = {
            'test_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter test name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter test description',
                'rows': 3
            }),
            'test_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


# Doctor - Add Medicine Form
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'medicine_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medicine name'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Twice a day'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Special instructions',
                'rows': 3
            }),
        }


# Doctor - Doctor Notes/Thoughts Form
class DoctorNotesForm(forms.ModelForm):
    class Meta:
        model = DoctorNotes
        fields = ['observations', 'diagnosis', 'treatment_plan', 'notes']
        widgets = {
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter observations',
                'rows': 4
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter diagnosis',
                'rows': 4
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter treatment plan',
                'rows': 4
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes',
                'rows': 3
            }),
        }


# Medical Report Form
class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['report_file', 'report_type', 'description']
        widgets = {
            'report_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'report_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Blood Test, X-Ray'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
                'rows': 3
            }),
        }


# Admin - Create Doctor User
class DoctorUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'


# Admin - Create Receptionist User
class ReceptionistUserCreationForm(DoctorUserCreationForm):
    pass


# Admin - Create Doctor Profile
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'license_number']
        widgets = {
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cardiology, Neurology'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical license number'
            }),
        }


# Reception - Patient Check-in/Visit Form
class PatientVisitForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = ['purpose', 'notes']
        widgets = {
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Checkup, Follow-up, Emergency'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes (optional)',
                'rows': 3
            }),
        }


# Test Report Upload Form
class TestReportForm(forms.ModelForm):
    class Meta:
        model = TestReport
        fields = ['test_type', 'report_file', 'test_date', 'notes']
        widgets = {
            'test_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Blood Test, X-Ray, Ultrasound'
            }),
            'report_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'test_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Test report notes (optional)',
                'rows': 3
            }),
        }
