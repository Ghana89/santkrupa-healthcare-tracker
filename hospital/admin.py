from django.contrib import admin
from .models import User, Patient, Doctor, Prescription, Test, Medicine, DoctorNotes, MedicalReport, PatientVisit, TestReport


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'patient_name', 'age', 'phone_number', 'status', 'registration_date']
    list_filter = ['status', 'registration_date']
    search_fields = ['patient_id', 'patient_name', 'phone_number']
    readonly_fields = ['patient_id', 'default_password', 'registration_date']
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_id', 'patient_name', 'age', 'phone_number', 'address')
        }),
        ('Account Details', {
            'fields': ('user', 'default_password')
        }),
        ('Status', {
            'fields': ('status', 'registration_date')
        }),
        ('Registration', {
            'fields': ('registered_by',)
        }),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'specialization', 'license_number']
    search_fields = ['user__first_name', 'user__last_name', 'specialization', 'license_number']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}"
    get_doctor_name.short_description = 'Name'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'prescription_date', 'status']
    list_filter = ['status', 'prescription_date']
    search_fields = ['patient__patient_name', 'doctor__user__first_name']
    readonly_fields = ['prescription_date']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'test_type', 'prescription', 'test_date', 'is_completed']
    list_filter = ['test_type', 'is_completed', 'test_date']
    search_fields = ['test_name', 'prescription__patient__patient_name']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'dosage', 'frequency', 'prescription']
    search_fields = ['medicine_name', 'prescription__patient__patient_name']


@admin.register(DoctorNotes)
class DoctorNotesAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'created_at', 'updated_at']
    search_fields = ['prescription__patient__patient_name', 'diagnosis']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'report_type', 'uploaded_at']
    list_filter = ['report_type', 'uploaded_at']
    search_fields = ['patient__patient_name', 'report_type']
    readonly_fields = ['uploaded_at']


@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'check_in_date', 'status', 'purpose', 'checked_in_by']
    list_filter = ['status', 'check_in_date']
    search_fields = ['patient__patient_name', 'purpose']
    readonly_fields = ['check_in_date']


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test_type', 'uploaded_at', 'test_date']
    list_filter = ['test_type', 'uploaded_at', 'test_date']
    search_fields = ['patient__patient_name', 'test_type']
    readonly_fields = ['uploaded_at']
