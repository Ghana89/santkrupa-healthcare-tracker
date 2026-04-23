# 📋 Complete Database Schema

## User Model
```python
Fields:
- id (Primary Key)
- username (CharField, unique)
- email (EmailField)
- first_name (CharField)
- last_name (CharField)
- password (CharField - hashed)
- role (CharField) - Choices: admin, doctor, receptionist, patient
- is_active (BooleanField)
- is_staff (BooleanField)
- is_superuser (BooleanField)
- created_at (DateTimeField)
- last_login (DateTimeField)
- date_joined (DateTimeField)
```

## Patient Model
```python
Fields:
- id (Primary Key, Auto-increment)
- patient_id (CharField, unique) - Auto-generated: PT[YEAR][5-DIGITS]
- user (OneToOneField to User, nullable)
- patient_name (CharField, max_length=100)
- age (IntegerField)
- address (TextField)
- phone_number (CharField, max_length=15)
- registration_date (DateField, auto_now_add=True)
- status (CharField) - Choices: registered, in_diagnosis, treatment_started, discharged
- default_password (CharField, max_length=20) - Auto-generated
- registered_by (ForeignKey to User with role='receptionist')

Example:
{
  "patient_id": "PT202600234",
  "patient_name": "John Doe",
  "age": 35,
  "address": "123 Main Street, City",
  "phone_number": "9876543210",
  "default_password": "aBc123Def",
  "status": "registered"
}
```

## Doctor Model
```python
Fields:
- id (Primary Key, Auto-increment)
- user (OneToOneField to User with role='doctor')
- specialization (CharField, max_length=100)
- license_number (CharField, max_length=50)

Example:
{
  "user": "Dr. John Doe",
  "specialization": "Cardiology",
  "license_number": "LIC123456"
}
```

## Prescription Model
```python
Fields:
- id (Primary Key, Auto-increment)
- patient (ForeignKey to Patient)
- doctor (ForeignKey to Doctor)
- prescription_date (DateTimeField, auto_now_add=True)
- status (CharField) - Choices: pending, completed, cancelled
- created_at (DateTimeField)

Example:
{
  "id": 1,
  "patient": "John Doe (PT202600234)",
  "doctor": "Dr. Jane Smith",
  "prescription_date": "2026-01-28 10:30:00",
  "status": "completed"
}
```

## Test Model
```python
Fields:
- id (Primary Key, Auto-increment)
- prescription (ForeignKey to Prescription)
- test_type (CharField) - Choices: blood, urine, xray, ultrasound, ecg, ct_scan, mri, other
- test_name (CharField, max_length=200)
- description (TextField, blank=True)
- test_date (DateField, nullable)
- result (TextField, blank=True)
- is_completed (BooleanField, default=False)

Example:
{
  "id": 1,
  "prescription": 1,
  "test_type": "blood",
  "test_name": "Complete Blood Count (CBC)",
  "description": "Routine blood test to check for infections",
  "test_date": "2026-01-29",
  "result": "All values within normal range",
  "is_completed": true
}
```

## Medicine Model
```python
Fields:
- id (Primary Key, Auto-increment)
- prescription (ForeignKey to Prescription)
- medicine_name (CharField, max_length=200)
- dosage (CharField, max_length=100)
- frequency (CharField, max_length=100)
- duration (CharField, max_length=100)
- instructions (TextField, blank=True)

Example:
{
  "id": 1,
  "prescription": 1,
  "medicine_name": "Aspirin",
  "dosage": "500mg",
  "frequency": "Twice daily",
  "duration": "7 days",
  "instructions": "Take with food. Avoid if allergic to aspirin"
}
```

## DoctorNotes Model
```python
Fields:
- id (Primary Key, Auto-increment)
- prescription (OneToOneField to Prescription)
- observations (TextField)
- diagnosis (TextField)
- treatment_plan (TextField)
- notes (TextField, blank=True)
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

Example:
{
  "prescription": 1,
  "observations": "Patient presented with mild chest pain and headaches",
  "diagnosis": "Mild hypertension with tension headaches",
  "treatment_plan": "Medication + Regular exercise + Dietary changes",
  "notes": "Follow-up appointment in 2 weeks"
}
```

## MedicalReport Model
```python
Fields:
- id (Primary Key, Auto-increment)
- patient (ForeignKey to Patient)
- report_file (FileField, upload_to='medical_reports/')
- report_type (CharField, max_length=50, blank=True)
- description (TextField, blank=True)
- uploaded_at (DateTimeField, default=timezone.now)

Example:
{
  "id": 1,
  "patient": "John Doe (PT202600234)",
  "report_file": "medical_reports/Blood_Test_Report_2026-01-28.pdf",
  "report_type": "Blood Test",
  "description": "Complete blood panel results",
  "uploaded_at": "2026-01-28 14:30:00"
}
```

---

## Database Relationships

```
User (1) ──────────── (1) Patient
User (1) ──────────── (1) Doctor
User (1) ──────────── (many) Prescription (as doctor)

Patient (1) ──────────── (many) Prescription
Patient (1) ──────────── (many) MedicalReport

Doctor (1) ──────────── (many) Prescription

Prescription (1) ──────────── (many) Test
Prescription (1) ──────────── (many) Medicine
Prescription (1) ──────────── (1) DoctorNotes
```

---

## Data Validation Rules

### Patient Registration
- patient_name: Required, max 100 characters
- age: Required, integer between 1-150
- address: Required, text field
- phone_number: Required, max 15 characters

### Prescription
- patient: Required
- doctor: Required
- Tests and medicines can be added after creation

### Test
- test_type: Required, must be from predefined list
- test_name: Required, max 200 characters
- test_date: Optional

### Medicine
- medicine_name: Required, max 200 characters
- dosage: Required, max 100 characters
- frequency: Required, max 100 characters
- duration: Required, max 100 characters

### Doctor Notes
- observations: Required
- diagnosis: Required
- treatment_plan: Required
- notes: Optional

---

## Index and Performance Optimization

**Indexed Fields:**
- Patient: patient_id (unique), registration_date
- User: username, role, email
- Prescription: prescription_date, status
- Test: test_date, is_completed
- MedicalReport: uploaded_at

---

## Storage Configuration

**Media Files Location:** `media/medical_reports/`  
**Static Files Location:** `static/`  
**Database File:** `db.sqlite3`  

---

## Constraints & Rules

1. One user can have only one patient profile
2. One user can have only one doctor profile
3. Prescription status follows: pending → completed → cancelled
4. Patient ID is unique and auto-generated
5. Doctor notes are one-to-one with prescription
6. Tests and medicines are dependent on prescription
7. Deleting prescription cascades to tests, medicines, notes
8. Deleting patient cascades to prescriptions, medical reports

