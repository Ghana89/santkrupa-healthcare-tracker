# Multi-Tenant API Design & Best Practices
## Quick Reference Guide

---

## 1. API Endpoint Structure

### 1.1 RESTful Endpoint Design

```
# Pattern: /api/v1/clinics/<clinic_id>/resource

GET    /api/v1/clinics/{clinic_id}/patients/                 # List all patients
POST   /api/v1/clinics/{clinic_id}/patients/                 # Create patient
GET    /api/v1/clinics/{clinic_id}/patients/{patient_id}/    # Get patient details
PUT    /api/v1/clinics/{clinic_id}/patients/{patient_id}/    # Update patient
DELETE /api/v1/clinics/{clinic_id}/patients/{patient_id}/    # Delete patient

GET    /api/v1/clinics/{clinic_id}/doctors/                  # List doctors
POST   /api/v1/clinics/{clinic_id}/consultations/            # Create consultation
GET    /api/v1/clinics/{clinic_id}/prescriptions/            # List prescriptions
POST   /api/v1/clinics/{clinic_id}/prescriptions/            # Create prescription

GET    /api/v1/clinics/{clinic_id}/analytics/dashboard/      # Dashboard metrics
GET    /api/v1/clinics/{clinic_id}/reports/daily/            # Daily reports
```

### 1.2 DRF Serializers with Tenant Validation

```python
# hospital/serializers.py

from rest_framework import serializers
from .models import Patient, Doctor, Prescription
from .middleware import get_current_clinic


class PatientSerializer(serializers.ModelSerializer):
    """Serialize patient with clinic validation"""
    
    clinic_id = serializers.IntegerField(read_only=True)
    doctor_name = serializers.CharField(source='registered_by.get_full_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'clinic_id', 'patient_id', 'patient_name', 'date_of_birth',
            'gender', 'blood_group', 'phone_number', 'email', 'address',
            'city', 'state', 'zip_code', 'emergency_contact_name',
            'emergency_contact_phone', 'status', 'doctor_name', 'registration_date'
        ]
        read_only_fields = ['patient_id', 'clinic_id', 'registration_date']
    
    def create(self, validated_data):
        """Ensure clinic_id is set from context"""
        clinic = get_current_clinic()
        validated_data['clinic'] = clinic
        return super().create(validated_data)


class DoctorSerializer(serializers.ModelSerializer):
    """Serialize doctor with clinic validation"""
    
    clinic_id = serializers.IntegerField(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'clinic_id', 'user', 'user_name', 'specialization',
            'license_number', 'qualification', 'experience_years'
        ]
        read_only_fields = ['clinic_id']


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serialize prescription"""
    
    clinic_id = serializers.IntegerField(read_only=True)
    patient_name = serializers.CharField(source='patient.patient_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    medicines = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'clinic_id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'prescription_date', 'status', 'notes', 'medicines'
        ]
        read_only_fields = ['clinic_id', 'prescription_date']
    
    def get_medicines(self, obj):
        """Get related medicines"""
        medicines = obj.medicines.all()
        return MedicineSerializer(medicines, many=True).data


class MedicineSerializer(serializers.ModelSerializer):
    """Serialize medicine"""
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'dosage', 'frequency', 'duration',
            'route', 'instructions', 'quantity', 'refills_allowed'
        ]
```

### 1.3 ViewSet with Multi-Tenant Security

```python
# hospital/api/viewsets.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .serializers import PatientSerializer, DoctorSerializer
from ..models import Patient, Doctor
from ..middleware import get_current_clinic


class MultiTenantViewSet(viewsets.ModelViewSet):
    """Base ViewSet with multi-tenant support"""
    
    permission_classes = [IsAuthenticated]
    
    def get_clinic(self):
        """Get clinic from URL parameter or user context"""
        clinic = get_current_clinic()
        if not clinic:
            clinic = self.request.user.clinic
        return clinic
    
    def get_queryset(self):
        """Filter queryset by current clinic"""
        clinic = self.get_clinic()
        return self.queryset_model.objects.filter(clinic=clinic)
    
    def perform_create(self, serializer):
        """Auto-set clinic on creation"""
        clinic = self.get_clinic()
        serializer.save(clinic=clinic)


class PatientViewSet(MultiTenantViewSet):
    """ViewSet for Patient management"""
    
    queryset_model = Patient
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    filterset_fields = ['status', 'gender']
    search_fields = ['patient_name', 'phone_number', 'patient_id']
    ordering_fields = ['registration_date', 'patient_name']
    ordering = ['-registration_date']
    
    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        """Get patient's medical history"""
        patient = self.get_object()
        
        # Verify patient belongs to current clinic
        clinic = self.get_clinic()
        if patient.clinic_id != clinic.id:
            raise PermissionDenied("Access denied")
        
        data = {
            'patient': PatientSerializer(patient).data,
            'visits': patient.visits.count(),
            'prescriptions': patient.prescriptions.count(),
            'test_reports': patient.test_reports.count(),
        }
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check-in patient for consultation"""
        patient = self.get_object()
        clinic = self.get_clinic()
        
        if patient.clinic_id != clinic.id:
            raise PermissionDenied("Access denied")
        
        # Create patient visit
        from ..models import PatientVisit
        visit = PatientVisit.objects.create(
            clinic=clinic,
            patient=patient,
            checked_in_by=request.user,
            purpose=request.data.get('purpose', '')
        )
        
        return Response({
            'success': True,
            'visit_id': visit.id,
            'token_number': visit.id,  # Generate proper token logic
            'message': 'Patient checked in successfully'
        })


class DoctorViewSet(MultiTenantViewSet):
    """ViewSet for Doctor management"""
    
    queryset_model = Doctor
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering_fields = ['user__first_name']
    
    @action(detail=True, methods=['get'])
    def queue(self, request, pk=None):
        """Get doctor's patient queue"""
        doctor = self.get_object()
        clinic = self.get_clinic()
        
        if doctor.clinic_id != clinic.id:
            raise PermissionDenied("Access denied")
        
        # Get pending visits for this doctor
        from ..models import PatientVisit
        pending_visits = PatientVisit.objects.filter(
            clinic=clinic,
            assigned_doctor=doctor,
            status='checked_in'
        ).order_by('check_in_date')
        
        from .serializers import PatientVisitSerializer
        serializer = PatientVisitSerializer(pending_visits, many=True)
        
        return Response({
            'doctor': DoctorSerializer(doctor).data,
            'queue': serializer.data,
            'queue_count': pending_visits.count()
        })
```

---

## 2. Permission Classes for Multi-Tenancy

### 2.1 Custom Permission Classes

```python
# hospital/api/permissions.py

from rest_framework import permissions
from ..middleware import get_current_clinic


class IsClinicUser(permissions.BasePermission):
    """Verify user belongs to the clinic in URL"""
    
    def has_permission(self, request, view):
        # Super users bypass
        if request.user.is_superuser:
            return True
        
        clinic = get_current_clinic()
        
        # Check if user belongs to this clinic
        return request.user.clinic_id == clinic.id


class IsClinicAdmin(permissions.BasePermission):
    """Only clinic admin can access"""
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        clinic = get_current_clinic()
        
        return (request.user.clinic_id == clinic.id and 
                request.user.role == 'admin')


class IsDoctor(permissions.BasePermission):
    """Only doctors can access"""
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        clinic = get_current_clinic()
        
        return (request.user.clinic_id == clinic.id and 
                request.user.role == 'doctor')


class IsReceptionist(permissions.BasePermission):
    """Only receptionists can access"""
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        clinic = get_current_clinic()
        
        return (request.user.clinic_id == clinic.id and 
                request.user.role == 'receptionist')


class OwnsObject(permissions.BasePermission):
    """Check if object belongs to user's clinic"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Check if object has clinic field
        if hasattr(obj, 'clinic'):
            return obj.clinic_id == request.user.clinic_id
        
        # Check if object has user.clinic
        if hasattr(obj, 'user') and hasattr(obj.user, 'clinic'):
            return obj.user.clinic_id == request.user.clinic_id
        
        return False
```

### 2.2 Apply Permissions to ViewSet

```python
# hospital/api/viewsets.py

from rest_framework import viewsets
from .permissions import IsClinicUser, IsDoctor, OwnsObject


class ConsultationViewSet(viewsets.ModelViewSet):
    """Consultation management"""
    
    permission_classes = [IsClinicUser, IsDoctor, OwnsObject]
    serializer_class = ConsultationSerializer
    
    def get_queryset(self):
        clinic = get_current_clinic()
        
        if self.request.user.role == 'doctor':
            # Doctors only see their own consultations
            return Consultation.objects.filter(
                clinic=clinic,
                doctor__user=self.request.user
            )
        else:
            # Clinic admins see all
            return Consultation.objects.filter(clinic=clinic)
```

---

## 3. Error Handling & Response Format

### 3.1 Standardized Response Format

```python
# hospital/api/responses.py

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Standardized API response helper"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return success response"""
        return Response({
            'success': True,
            'message': message,
            'data': data,
            'error': None
        }, status=status_code)
    
    @staticmethod
    def error(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return error response"""
        return Response({
            'success': False,
            'message': message,
            'data': None,
            'errors': errors or {}
        }, status=status_code)
    
    @staticmethod
    def paginated(queryset, serializer_class, request, context=None):
        """Return paginated response"""
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(page, many=True, context=context)
        
        return paginator.get_paginated_response({
            'success': True,
            'data': serializer.data
        })


# Usage in ViewSet
class PatientViewSet(viewsets.ModelViewSet):
    
    def list(self, request, *args, **kwargs):
        """List patients with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(
            queryset,
            self.serializer_class,
            request,
            context={'request': request}
        )
    
    def create(self, request, *args, **kwargs):
        """Create patient"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return APIResponse.success(
                data=serializer.data,
                message="Patient created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            return APIResponse.error(
                message="Validation error",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST
            )
```

### 3.2 Exception Handler

```python
# hospital/api/exceptions.py

from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for multi-tenant errors"""
    
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'message': response.data.get('detail', 'An error occurred'),
            'data': None,
            'errors': response.data if not response.data.get('detail') else None
        }
    
    return response


# Add to settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'hospital.api.exceptions.custom_exception_handler',
    'PAGE_SIZE': 50,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## 4. Authentication & Token Management

### 4.1 JWT Authentication for APIs

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt',
]

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
    ),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 4.2 Token Endpoint with Clinic Context

```python
# hospital/api/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with clinic context"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['clinic_id'] = user.clinic.id
        token['clinic_name'] = user.clinic.name
        token['role'] = user.role
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['clinic_id'] = self.user.clinic.id
        data['clinic_name'] = self.user.clinic.name
        data['username'] = self.user.username
        data['role'] = self.user.role
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

---

## 5. Versioning Strategy

### 5.1 API Version Management

```python
# santkrupa_hospital/urls.py

from rest_framework.routers import DefaultRouter
from hospital.api.viewsets import PatientViewSet, DoctorViewSet

router = DefaultRouter()

urlpatterns = [
    # API v1
    path('api/v1/clinics/<int:clinic_id>/', include([
        path('auth/', include([
            path('token/', views.CustomTokenObtainPairView.as_view()),
            path('refresh/', TokenRefreshView.as_view()),
        ])),
        path('patients/', PatientViewSet.as_view({'get': 'list', 'post': 'create'})),
        path('patients/<int:pk>/', PatientViewSet.as_view({
            'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
        })),
        path('doctors/', DoctorViewSet.as_view({'get': 'list'})),
    ])),
]
```

---

## 6. Rate Limiting

### 6.1 Per-Clinic Rate Limiting

```python
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'clinic': '5000/hour',  # Per clinic
    }
}
```

### 6.2 Custom Throttle Class

```python
# hospital/api/throttles.py

from rest_framework.throttling import UserRateThrottle


class ClinicRateThrottle(UserRateThrottle):
    """Rate throttle per clinic"""
    
    scope = 'clinic'
    
    def get_cache_key(self):
        if self.request.user.is_authenticated:
            # Throttle per clinic, not per user
            return f'clinic_{self.request.user.clinic_id}_throttle'
        
        return None
```

---

## 7. Documentation & Swagger

### 7.1 API Documentation

```python
# settings.py

INSTALLED_APPS = [
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

### 7.2 ViewSet Documentation

```python
class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patients within a clinic.
    
    list:
        Get all patients for current clinic
    
    create:
        Create a new patient
    
    retrieve:
        Get specific patient details
    
    update:
        Update patient information
    
    destroy:
        Delete a patient
    """
    
    def list(self, request, *args, **kwargs):
        """
        Get list of all patients in current clinic.
        
        Query Parameters:
            - status: Filter by patient status
            - gender: Filter by gender
            - search: Search by name or phone number
            - ordering: Order by field
        """
        pass
```

---

## 8. Monitoring & Logging

### 8.1 API Logging

```python
# hospital/api/logging.py

import logging
import json
from rest_framework.response import Response


logger = logging.getLogger('hospital_api')


class APILoggingMiddleware:
    """Log all API requests/responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        logger.info(f"API Request: {request.method} {request.path}")
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"  User: {request.user.username} (Clinic: {request.user.clinic.name})")
        
        response = self.get_response(request)
        
        # Log response
        logger.info(f"  Response: {response.status_code}")
        
        return response
```

---

## 9. Testing API Endpoints

### 9.1 API Test Cases

```python
# hospital/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model


class PatientAPITestCase(APITestCase):
    """Test patient API endpoints"""
    
    def setUp(self):
        """Setup test clinics and users"""
        from hospital.models import Clinic
        
        User = get_user_model()
        
        self.clinic = Clinic.objects.create(
            name='Test Clinic',
            slug='test-clinic',
            email='test@clinic.com',
            phone_number='1234567890',
            address='Test Address',
            city='Test City',
            state='Test State',
            zip_code='123456',
            registration_number='REG-123456',
            gstin='GSTIN123456',
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            clinic=self.clinic,
            role='admin'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            password='testpass123',
            clinic=self.clinic,
            role='doctor'
        )
        
        self.receptionist_user = User.objects.create_user(
            username='receptionist',
            password='testpass123',
            clinic=self.clinic,
            role='receptionist'
        )
    
    def test_patient_list_requires_authentication(self):
        """Test that patient list requires authentication"""
        response = self.client.get('/api/v1/clinics/1/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_receptionist_can_list_patients(self):
        """Test receptionist can list patients"""
        self.client.force_authenticate(user=self.receptionist_user)
        response = self.client.get('/api/v1/clinics/1/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_patient_as_receptionist(self):
        """Test receptionist can create patient"""
        self.client.force_authenticate(user=self.receptionist_user)
        
        data = {
            'patient_name': 'John Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'phone_number': '9876543210',
            'address': 'Test Address',
            'city': 'Test City',
            'state': 'Test State',
            'zip_code': '123456',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '9876543210',
            'identification_type': 'Aadhaar',
            'identification_number': '123456789012',
        }
        
        response = self.client.post('/api/v1/clinics/1/patients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
```

---

## 10. Security Best Practices Checklist

- [ ] Always validate clinic_id matches user's clinic
- [ ] Use permission classes on all viewsets
- [ ] Filter QuerySets by clinic automatically
- [ ] Validate clinic_id in serializers
- [ ] Use JWT tokens for API authentication
- [ ] Implement rate limiting per clinic
- [ ] Log all API access and modifications
- [ ] Use HTTPS in production
- [ ] Validate input data thoroughly
- [ ] Return minimal error information
- [ ] Use strong password policies
- [ ] Implement audit trails
- [ ] Regular security audits

---

