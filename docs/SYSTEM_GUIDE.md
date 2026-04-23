# SantKrupa Hospital - Healthcare Management System

## Complete Setup & Usage Guide

### System Overview
The system has been completely rebuilt with a comprehensive workflow for:
- **Reception**: Patient registration
- **Doctor**: Prescription management (tests, medicines, notes)
- **Patient**: View prescriptions and upload medical reports
- **Admin**: Manage users and system

---

## Quick Start Guide

### 1. **Initial Setup** (First Time Only)

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser (admin):
```bash
python manage.py createsuperuser
```

Start the server:
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

---

### 2. **User Roles & Their Workflows**

#### **RECEPTIONIST**
**Responsibilities:**
- Register new patients
- Collect patient information (name, age, address, phone)
- View patient records
- Provide credentials to patients

**Workflow:**
1. Login with receptionist credentials
2. Click "Register New Patient"
3. Fill patient details (auto-generates Patient ID & password)
4. Share credentials with patient
5. View patient history anytime

**Login URL:** `http://127.0.0.1:8000/login/`

---

#### **DOCTOR**
**Responsibilities:**
- Create prescriptions for registered patients
- Prescribe tests (blood test, X-ray, ultrasound, etc.)
- Prescribe medicines with dosage details
- Record observations, diagnosis, and treatment plan
- Complete prescriptions

**Workflow:**
1. Login with doctor credentials
2. View all patients on dashboard
3. Click "Create Prescription" for a patient
4. Add tests (type, name, date)
5. Add medicines (name, dosage, frequency, duration)
6. Record doctor's notes (observations, diagnosis, treatment plan)
7. Complete the prescription

**Key Fields:**
- **Tests**: Test name, type, date, description, result, completion status
- **Medicines**: Name, dosage, frequency, duration, instructions
- **Doctor Notes**: Observations, diagnosis, treatment plan, additional notes

---

#### **PATIENT**
**Responsibilities:**
- View prescriptions from doctors
- See prescribed tests and medicines
- Read doctor's notes and observations
- Upload medical reports/documents

**Workflow:**
1. Login using Patient ID as username and auto-generated password
2. View dashboard with prescriptions and reports
3. Click on prescriptions to see:
   - All prescribed tests and their status
   - Medicines with dosage and frequency
   - Doctor's observations and treatment plan
4. Upload medical documents anytime

---

#### **ADMIN**
**Responsibilities:**
- Create doctor accounts with specialization
- Create receptionist accounts
- View all patients and doctors
- Manage system users

**Workflow:**
1. Login with admin credentials
2. View statistics (total patients, doctors, prescriptions)
3. Create new doctors (name, specialization, license)
4. Create new receptionists (name, credentials)
5. View all patients and doctors
6. Access Django admin panel for advanced management

**Admin URL:** `http://127.0.0.1:8000/admin-dashboard/`

---

## Database Models

### 1. **User Model**
```
- username (unique)
- email
- first_name, last_name
- password
- role (admin/doctor/receptionist/patient)
- created_at
```

### 2. **Patient Model**
```
- patient_id (auto-generated: PT + Year + 5 digits)
- patient_name
- age
- address
- phone_number
- registration_date
- status (registered/in_diagnosis/treatment_started/discharged)
- default_password (auto-generated)
- registered_by (receptionist who registered)
```

### 3. **Doctor Model**
```
- user (OneToOne with User)
- specialization (Cardiology, Neurology, etc.)
- license_number
```

### 4. **Prescription Model**
```
- patient (ForeignKey)
- doctor (ForeignKey)
- prescription_date
- status (pending/completed/cancelled)
```

### 5. **Test Model**
```
- prescription (ForeignKey)
- test_type (blood, urine, xray, ultrasound, ecg, ct_scan, mri, other)
- test_name
- description
- test_date
- result
- is_completed
```

### 6. **Medicine Model**
```
- prescription (ForeignKey)
- medicine_name
- dosage
- frequency (e.g., "Twice a day")
- duration (e.g., "7 days")
- instructions
```

### 7. **DoctorNotes Model**
```
- prescription (OneToOne)
- observations
- diagnosis
- treatment_plan
- notes
- created_at, updated_at
```

### 8. **MedicalReport Model**
```
- patient (ForeignKey)
- report_file
- report_type
- description
- uploaded_at
```

---

## URL Routes

### Authentication
- `GET/POST /login/` - Login page
- `GET /logout/` - Logout

### Homepage
- `GET /` - Homepage with all portals

### Reception
- `GET /reception/dashboard/` - Reception dashboard
- `GET/POST /reception/register-patient/` - Register new patient
- `GET /reception/patient/<id>/` - View patient details

### Doctor
- `GET /doctor/dashboard/` - Doctor dashboard
- `GET/POST /doctor/create-prescription/<patient_id>/` - Create prescription
- `GET/POST /doctor/prescription/<prescription_id>/` - Add tests, medicines, notes
- `GET/POST /doctor/prescription/<prescription_id>/complete/` - Complete prescription
- `GET /doctor/test/<test_id>/delete/` - Delete test
- `GET /doctor/medicine/<medicine_id>/delete/` - Delete medicine

### Patient
- `GET /patient/dashboard/` - Patient dashboard
- `GET /patient/prescription/<prescription_id>/` - View prescription details
- `GET/POST /patient/upload-report/` - Upload medical report

### Admin
- `GET /admin-dashboard/` - Admin dashboard
- `GET/POST /admin/create-doctor/` - Create doctor account
- `GET/POST /admin/create-receptionist/` - Create receptionist
- `GET /admin/all-patients/` - View all patients
- `GET /admin/all-doctors/` - View all doctors
- `GET /admin/` - Django admin panel (superuser only)

---

## How to Create Test Accounts

### 1. Create Admin (Via CLI)
```bash
python manage.py createsuperuser
```

### 2. Create Doctor (Via Web)
1. Login as admin
2. Go to Admin Dashboard
3. Click "Create Doctor Account"
4. Fill doctor details and credentials
5. Doctor can login immediately

### 3. Create Receptionist (Via Web)
1. Login as admin
2. Go to Admin Dashboard
3. Click "Create Receptionist Account"
4. Fill receptionist details and credentials
5. Receptionist can start registering patients

### 4. Create Patient (Via Reception)
1. Login as receptionist
2. Click "Register New Patient"
3. Fill patient details
4. System auto-generates:
   - **Patient ID**: e.g., PT202600001
   - **Default Password**: e.g., aB3cD9eF
5. Provide these credentials to patient

---

## Feature Highlights

✅ **Patient Registration**
- Auto-generated unique Patient ID
- Auto-generated secure password
- Complete patient information storage

✅ **Prescription Management**
- Create prescriptions for any patient
- Add multiple tests with scheduling
- Add medicines with dosage details
- Record doctor's clinical notes

✅ **Medical Records**
- Patients can upload medical reports
- Doctors can view patient reports
- Digital storage with timestamps

✅ **Secure Access**
- Role-based authentication
- Login required for all portals
- Auto-redirect based on user role

✅ **Professional UI**
- Modern, hospital-grade design
- Responsive across devices
- Intuitive navigation
- Color-coded status indicators

---

## Common Workflows

### Complete Patient Care Workflow:

**1. Reception (Day 1)**
```
Receptionist → Registers patient → Gets Patient ID & Password
                                 → Provides to patient
```

**2. Doctor (Day 1-2)**
```
Doctor → Views patient on dashboard
      → Creates prescription
      → Adds required tests (scheduled for future)
      → Prescribes medicines
      → Records clinical notes
      → Completes prescription
```

**3. Patient (Ongoing)**
```
Patient → Views prescription on portal
       → Sees tests to complete (with dates)
       → Gets medicines list (with dosage)
       → Reads doctor's diagnosis
       → Can upload additional medical reports
```

**4. Follow-up (Doctor)**
```
Doctor → Reviews patient's uploaded reports
      → Creates new prescription if needed
      → Updates treatment plan
```

---

## Troubleshooting

**Q: Page shows "Not Found" when accessing restricted pages?**
A: You need to login first. Go to `/login/` with your credentials.

**Q: Patient can't login?**
A: Check the Patient ID and password provided at registration. Patient ID is in format: `PT + Year + 5 digits` (e.g., PT202600001)

**Q: Doctor can't create prescription?**
A: Ensure doctor profile is created with specialization and license number.

**Q: Can't access admin panel?**
A: Use superuser credentials created with `createsuperuser` command.

---

## System Architecture

```
┌─────────────────────────────────────┐
│         Homepage (Public)             │
├─────────────────────────────────────┤
│                                       │
├─→ Reception Portal ─→ Register Patient
│   (receptionist login)     │
│                           └─→ Generate Patient ID & Password
│
├─→ Doctor Portal ─→ Create Prescription
│   (doctor login)    ├─→ Add Tests
│                     ├─→ Add Medicines
│                     └─→ Add Doctor Notes
│
├─→ Patient Portal ─→ View Prescriptions
│   (patient login)    ├─→ See Tests & Medicines
│                      └─→ Upload Medical Reports
│
└─→ Admin Portal ─→ Manage Users
    (admin login)    ├─→ Create Doctors
                     ├─→ Create Receptionists
                     └─→ View Statistics
```

---

## Next Steps

1. ✅ Complete system setup
2. ✅ Create test accounts for each role
3. ✅ Test complete workflow
4. ✅ Customize with real hospital details (contact info, etc.)
5. ✅ Deploy to production server

---

**System Version:** 1.0.0  
**Last Updated:** January 28, 2026  
**Created for:** SantKrupa Hospital
