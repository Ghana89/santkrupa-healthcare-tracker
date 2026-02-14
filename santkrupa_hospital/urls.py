"""
URL configuration for santkrupa_hospital project - Multi-tenant enabled
"""
from django.contrib import admin
from django.urls import path, include
from hospital import views

# Clinic-specific URL patterns
clinic_urlpatterns = [
    # Clinic-specific authentication
    path('login/', views.login_view, name='login'),

    # Reception
    path('reception/dashboard/', views.reception_dashboard, name='reception_dashboard'),
    path('reception/register-patient/', views.register_patient, name='register_patient'),
    path('reception/patient-search/', views.patient_search, name='patient_search'),
    path('reception/checkin-dashboard/', views.checkin_dashboard, name='checkin_dashboard'),
    path('reception/patient/<int:patient_id>/', views.view_patient_details, name='patient_details'),
    path('reception/patient/<int:patient_id>/upload-report/', views.receptionist_upload_medical_report, name='receptionist_upload_medical_report'),
    path('reception/patient-checkin/', views.patient_checkin, name='patient_checkin'),
    path('reception/patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    
    # Doctor
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/prescription-tracking/', views.doctor_prescription_tracking, name='doctor_prescription_tracking'),
    path('doctor/create-prescription/<int:patient_id>/', views.create_prescription, name='create_prescription'),
    path('doctor/prescription/<int:prescription_id>/', views.add_prescription_details, name='add_prescription_details'),
    path('doctor/prescription/<int:prescription_id>/complete/', views.complete_prescription, name='complete_prescription'),
    path('doctor/prescription/<int:prescription_id>/print/', views.print_prescription, name='print_prescription'),
    path('doctor/test/<int:test_id>/delete/', views.delete_test, name='delete_test'),
    path('doctor/medicine/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),
    path('doctor/patient-history/<int:patient_id>/', views.patient_history, name='patient_history'),
    
    # Admissions & Hospitalization
    path('doctor/admit-patient/<int:patient_id>/', views.admit_patient, name='admit_patient'),
    path('doctor/admission/<int:admission_id>/', views.admission_details, name='admission_details'),
    path('doctor/admission/<int:admission_id>/add-treatment/', views.add_treatment, name='add_treatment'),
    path('doctor/admission/<int:admission_id>/upload-report/', views.upload_admission_report, name='upload_admission_report'),
    path('doctor/admission/<int:admission_id>/update-status/', views.update_admission_status, name='update_admission_status'),
    path('doctor/patient/<int:patient_id>/admissions/', views.patient_admissions, name='patient_admissions'),
    path('doctor/admissions-dashboard/', views.admissions_dashboard, name='admissions_dashboard'),
    path('doctor/prescription/<int:prescription_id>/recommend-admission/', views.recommend_admission, name='recommend_admission'),
    path('doctor/admission-recommendations/', views.admission_recommendations, name='admission_recommendations'),
    
    # Patient
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/prescription/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('patient/prescription/<int:prescription_id>/print/', views.print_prescription, name='print_prescription_patient'),
    path('patient/upload-report/', views.upload_medical_report, name='upload_medical_report'),
    path('patient/upload-test-report/', views.upload_test_report, name='upload_test_report'),
    path('patient/test-reports/', views.view_test_reports, name='view_test_reports'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/create-doctor/', views.create_doctor, name='create_doctor'),
    path('admin-dashboard/create-receptionist/', views.create_receptionist, name='create_receptionist'),
    path('admin-dashboard/all-patients/', views.view_all_patients, name='view_all_patients'),
    path('admin-dashboard/all-doctors/', views.view_all_doctors, name='view_all_doctors'),
    path('admin-dashboard/all-receptionists/', views.view_all_receptionists, name='view_all_receptionists'),
    path('admin-dashboard/doctor/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    path('admin-dashboard/receptionist/<int:user_id>/delete/', views.delete_receptionist, name='delete_receptionist'),
    
    # Master Data Management
    path('admin-dashboard/manage-medicines/', views.manage_master_medicines, name='manage_master_medicines'),
    path('admin-dashboard/delete-medicine/<int:medicine_id>/', views.delete_master_medicine, name='delete_master_medicine'),
    path('admin-dashboard/manage-tests/', views.manage_master_tests, name='manage_master_tests'),
    path('admin-dashboard/delete-test/<int:test_id>/', views.delete_master_test, name='delete_master_test'),
    path('api/master-medicines/', views.api_master_medicines, name='api_master_medicines'),
    path('api/master-tests/', views.api_master_tests, name='api_master_tests'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication (Global)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_patient, name='register'),  # Public registration
    path('register-clinic/', views.register_clinic, name='register_clinic'),

    # Global AJAX endpoint for patient search (also exposed under clinic/<slug>/)
    path('reception/patient-search/', views.patient_search, name='patient_search_global'),
    path('reception/checkin-dashboard/', views.checkin_dashboard, name='checkin_dashboard_global'),
    
    # Superadmin (Global)
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/clinic/<int:clinic_id>/delete/', views.delete_clinic, name='delete_clinic'),
    path('superadmin/clinic/<int:clinic_id>/patients/', views.superadmin_clinic_patients, name='superadmin_clinic_patients'),
    path('superadmin/clinic/<int:clinic_id>/doctors/', views.superadmin_clinic_doctors, name='superadmin_clinic_doctors'),
    path('superadmin/clinic/<int:clinic_id>/prescriptions/', views.superadmin_clinic_prescriptions, name='superadmin_clinic_prescriptions'),
    
    # Public pages (Global)
    path('', views.homepage, name='homepage'),
    
    # Multi-tenant clinic URLs
    path('clinic/<slug:clinic_slug>/', include(clinic_urlpatterns)),
]

# Serve media files in development
from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
