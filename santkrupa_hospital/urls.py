"""
URL configuration for santkrupa_hospital project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('register/', views.register_patient, name='register_patient'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('upload-report/', views.upload_medical_report, name='upload_medical_report'),
    path('download-prescription/<int:prescription_id>/', views.download_prescription, name='download_prescription'),
]
