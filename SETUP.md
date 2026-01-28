# SantKrupa Hospital - First Time Setup Instructions

## Prerequisites
- Python 3.8+ installed
- Virtual environment activated
- Django 5.2+ installed

---

## Step 1: Database Setup

Run migrations to create all database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 2: Create Superuser (Admin)

Create your first admin account:
```bash
python manage.py createsuperuser
```

You'll be prompted for:
- **Username**: admin (or your choice)
- **Email**: admin@santkrupahospital.com
- **Password**: (enter a strong password)
- **Password (again)**: (confirm)

Remember these credentials - you'll need them to login to the admin portal.

---

## Step 3: Start the Development Server

```bash
python manage.py runserver
```

Server will start at: **http://127.0.0.1:8000/**

---

## Step 4: Initial Logins

### 4.1 Login as Admin
```
URL: http://127.0.0.1:8000/login/
Username: admin (your superuser username)
Password: (your superuser password)
```

### 4.2 Create First Doctor Account
1. Click "Admin Portal" on homepage
2. Or go to: http://127.0.0.1:8000/admin-dashboard/
3. Click "Create Doctor Account"
4. Fill in details:
   - **Username**: doctor1
   - **First Name**: John
   - **Last Name**: Doe
   - **Email**: doctor1@santkrupahospital.com
   - **Specialization**: Cardiology
   - **License Number**: MCI-12345
   - **Password**: (strong password)
5. Doctor can now login with username: `doctor1`

### 4.3 Create First Receptionist Account
1. Go back to Admin Dashboard
2. Click "Create Receptionist Account"
3. Fill in details:
   - **Username**: reception1
   - **First Name**: Jane
   - **Last Name**: Smith
   - **Email**: reception1@santkrupahospital.com
   - **Password**: (strong password)
4. Receptionist can now login with username: `reception1`

---

## Step 5: Test Complete Workflow

### Phase 1: Register a Patient (As Receptionist)
1. **Login**: http://127.0.0.1:8000/login/
   - Username: `reception1`
   - Password: (your receptionist password)

2. **Register Patient**:
   - Click "Reception Dashboard"
   - Click "Register New Patient"
   - Fill details:
     - **Name**: Raj Kumar
     - **Age**: 45
     - **Phone**: 9876543210
     - **Address**: 123 Main Street, City
   - Click "Register Patient"

3. **Note Down Credentials**:
   - **Patient ID**: (auto-generated, e.g., PT202600001)
   - **Password**: (auto-generated, e.g., aB3cD9eF)

### Phase 2: Create Prescription (As Doctor)
1. **Login**: http://127.0.0.1:8000/login/
   - Username: `doctor1`
   - Password: (your doctor password)

2. **Create Prescription**:
   - Click "Doctor Dashboard"
   - Find "Raj Kumar" in the patient list
   - Click "Create Prescription"
   - Confirm creation

3. **Add Tests**:
   - Fill Test Name: "Complete Blood Count"
   - Select Test Type: "Blood Test"
   - Set Test Date: (future date)
   - Click "+ Add Test"
   - Repeat for more tests

4. **Add Medicines**:
   - Fill Medicine Name: "Aspirin"
   - Dosage: "100mg"
   - Frequency: "Once daily"
   - Duration: "7 days"
   - Click "+ Add Medicine"
   - Repeat for more medicines

5. **Add Doctor Notes**:
   - **Observations**: Patient shows high blood pressure
   - **Diagnosis**: Hypertension
   - **Treatment Plan**: Start medication, regular monitoring, salt restriction diet
   - Click "💾 Save Notes"

6. **Complete Prescription**:
   - Review all tests and medicines
   - Click "✓ Complete Prescription"

### Phase 3: View Prescription (As Patient)
1. **Login**: http://127.0.0.1:8000/login/
   - Username: `PT202600001` (patient ID)
   - Password: `aB3cD9eF` (auto-generated password)

2. **View Dashboard**:
   - Click "Patient Dashboard"
   - See prescription from Dr. John Doe
   - Click prescription to view details

3. **See Complete Information**:
   - All prescribed tests with dates
   - All medicines with dosage and frequency
   - Doctor's observations and diagnosis
   - Treatment plan details

4. **Upload Medical Report** (Optional):
   - Click "Upload New Report"
   - Upload a medical document
   - Add description
   - File saved securely

---

## URL Quick Reference

| Role | Login | Dashboard |
|------|-------|-----------|
| **Admin** | /login/ | /admin-dashboard/ |
| **Doctor** | /login/ | /doctor/dashboard/ |
| **Receptionist** | /login/ | /reception/dashboard/ |
| **Patient** | /login/ | /patient/dashboard/ |

---

## Default Test Credentials Template

Save these for quick testing:

```
ADMIN:
Username: admin
Password: (your chosen password)

DOCTOR 1:
Username: doctor1
Password: (your chosen password)
Specialization: Cardiology

RECEPTIONIST 1:
Username: reception1
Password: (your chosen password)

PATIENT 1 (Auto-generated):
Username: PT202600001
Password: aB3cD9eF
```

---

## Key Features to Test

✅ Patient registration with auto-generated ID
✅ Doctor prescription creation
✅ Multiple tests per prescription
✅ Multiple medicines per prescription
✅ Doctor's notes (observations, diagnosis, treatment plan)
✅ Patient viewing all prescription details
✅ Medical report upload
✅ Role-based access control
✅ Logout functionality

---

## Troubleshooting

**Server won't start?**
- Ensure Python is in your PATH
- Activate virtual environment: `.venv\Scripts\Activate.ps1`
- Check all migrations: `python manage.py showmigrations`

**Can't login?**
- Double-check username and password
- Ensure account was created successfully
- Check that user role is correct

**Getting 404 errors?**
- Ensure server is running (`http://127.0.0.1:8000/`)
- Check URL paths match exactly
- Clear browser cache if needed

**Database errors?**
- Delete `db.sqlite3` and run migrations again
- Ensure migrations folder exists
- Run: `python manage.py migrate --run-syncdb`

---

## Next Steps After Testing

1. Change admin password to strong secure password
2. Set up real hospital contact details (edit homepage)
3. Create more doctor and receptionist accounts
4. Test with multiple patients
5. Set up email notifications (future feature)
6. Deploy to production server

---

**Happy Testing! 🏥**

For more details, see: `SYSTEM_GUIDE.md`
