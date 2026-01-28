"""
URL configuration for santkrupa_hospital project.
"""
from django.contrib import admin
from django.urls import path
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Public
    path('', views.homepage, name='homepage'),
    
    # Reception
    path('reception/dashboard/', views.reception_dashboard, name='reception_dashboard'),
    path('reception/register-patient/', views.register_patient, name='register_patient'),
    path('reception/patient/<int:patient_id>/', views.view_patient_details, name='patient_details'),
    path('reception/patient-checkin/', views.patient_checkin, name='patient_checkin'),
    path('reception/patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    
    # Doctor
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/create-prescription/<int:patient_id>/', views.create_prescription, name='create_prescription'),
    path('doctor/prescription/<int:prescription_id>/', views.add_prescription_details, name='add_prescription_details'),
    path('doctor/prescription/<int:prescription_id>/complete/', views.complete_prescription, name='complete_prescription'),
    path('doctor/prescription/<int:prescription_id>/print/', views.print_prescription, name='print_prescription'),
    path('doctor/test/<int:test_id>/delete/', views.delete_test, name='delete_test'),
    path('doctor/medicine/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),
    path('doctor/patient-history/<int:patient_id>/', views.patient_history, name='patient_history'),
    
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
]
