# 🏥 SantKrupa Hospital Management System

A complete hospital management system built with Django. This system facilitates patient registration, doctor consultations, prescription management, and medical record tracking.

## 📋 System Overview

The system has four main roles:

### 1. **Reception Staff**
- Register new patients with personal information
- Auto-generate unique Patient ID and login credentials
- View and manage patient records
- Access patient details and history

### 2. **Doctor**
- View all registered patients
- Create prescriptions for patients
- Prescribe tests (blood test, ultrasound, X-Ray, etc.)
- Prescribe medicines with dosage and frequency
- Record observations, diagnosis, and treatment plans
- Complete prescriptions for patient access

### 3. **Patient**
- View assigned prescriptions
- Access prescribed tests and medicines
- Upload medical reports and documents
- Track health status
- View doctor's notes and recommendations

### 4. **Admin**
- Create doctor accounts with specialization
- Create receptionist accounts
- View system statistics
- Manage all users and records
- Access Django admin panel

## 🚀 Getting Started

### Installation

1. **Clone or extract the project**
```bash
cd santkrupa-healthcare-tracker
```

2. **Activate virtual environment**
```bash
# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py migrate
```

5. **Create a superuser (Admin)**
```bash
python setup_admin.py
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Access the application**
- Homepage: `http://localhost:8000/`
- Admin Panel: `http://localhost:8000/admin/`

## 📝 Default Credentials

### Admin Account
- **Username:** admin
- **Password:** admin123
- **Role:** Admin

> ⚠️ **Note:** Change the admin password immediately after first login!

## 🔄 Workflow

### Patient Registration Flow

```
1. Reception Staff Login
   ↓
2. Register New Patient
   - Enter patient name, age, address, phone
   - System auto-generates Patient ID
   - System auto-generates default password
   ↓
3. Provide credentials to patient
```

### Prescription Flow

```
1. Doctor Views Patients
   ↓
2. Doctor Creates Prescription
   - Select patient
   - Add tests (blood test, ultrasound, etc.)
   - Add medicines (name, dosage, frequency)
   - Add doctor's notes (observations, diagnosis, treatment plan)
   ↓
3. Complete Prescription
   ↓
4. Patient Receives Notification
   ↓
5. Patient Views All Details in Portal
```

### Patient View Flow

```
1. Patient Login with credentials
   ↓
2. View Dashboard
   - See all prescriptions
   - View medical reports
   ↓
3. View Prescription Details
   - See prescribed tests
   - See medicines with instructions
   - Read doctor's notes
   ↓
4. Upload Medical Reports
   - Share documents with doctor
```

## 📊 Database Models

### User Model
- Custom user model with role-based access
- Roles: admin, doctor, receptionist, patient

### Patient Model
- patient_id (auto-generated)
- patient_name, age, address, phone_number
- registration_date, status
- default_password (auto-generated)

### Doctor Model
- Linked to User model
- specialization, license_number

### Prescription Model
- Linked to Patient and Doctor
- Status: pending, completed, cancelled
- Contains tests, medicines, and notes

### Test Model
- Test type (blood, urine, x-ray, ultrasound, ecg, ct_scan, mri)
- test_date, result, is_completed

### Medicine Model
- medicine_name, dosage, frequency, duration
- instructions

### DoctorNotes Model
- observations, diagnosis, treatment_plan, notes

### MedicalReport Model
- report_file, report_type, description
- uploaded_at

## 🔐 Security Features

- Role-based access control
- User authentication required for all sensitive operations
- CSRF protection on all forms
- Secure password handling
- Auto-generated patient credentials

## 📂 Project Structure

```
santkrupa-healthcare-tracker/
├── hospital/
│   ├── models.py              # Database models
│   ├── views.py               # Application views
│   ├── forms.py               # Form definitions
│   ├── admin.py               # Admin configuration
│   ├── templates/
│   │   ├── hospital/
│   │   │   ├── base.html
│   │   │   ├── homepage.html
│   │   │   ├── reception/     # Reception templates
│   │   │   ├── doctor/        # Doctor templates
│   │   │   ├── patient/       # Patient templates
│   │   │   └── admin/         # Admin templates
├── santkrupa_hospital/
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── static/                    # CSS and JavaScript
├── media/                     # Uploaded files
├── manage.py
├── requirements.txt
└── README.md
```

## 🔗 URL Routes

### Public
- `/` - Homepage
- `/admin/` - Django admin panel

### Reception
- `/reception/dashboard/` - Reception dashboard
- `/reception/register-patient/` - Patient registration form
- `/reception/patient/<id>/` - View patient details

### Doctor
- `/doctor/dashboard/` - Doctor dashboard
- `/doctor/create-prescription/<patient_id>/` - Create prescription
- `/doctor/prescription/<prescription_id>/` - Edit prescription (add tests, medicines, notes)
- `/doctor/prescription/<prescription_id>/complete/` - Complete prescription

### Patient
- `/patient/dashboard/` - Patient dashboard
- `/patient/prescription/<prescription_id>/` - View prescription details
- `/patient/upload-report/` - Upload medical report

### Admin
- `/admin-dashboard/` - Admin dashboard
- `/admin/create-doctor/` - Create doctor account
- `/admin/create-receptionist/` - Create receptionist account
- `/admin/all-patients/` - View all patients
- `/admin/all-doctors/` - View all doctors

## 🎨 User Interface

The system features:
- Professional hospital app-like design
- Responsive layout (mobile-friendly)
- Color-coded status indicators
- Intuitive navigation
- Role-based dashboards
- Easy-to-use forms

## 📞 Support

For issues or questions, please contact:
- Email: info@santkrupahospital.com
- Phone: +91-XXXX-XXXX-XX
- Emergency: +91-XXXX-XXXX-XX

## ⚖️ License

This project is proprietary to SantKrupa Hospital.

---

**Version:** 1.0.0  
**Last Updated:** January 2026
