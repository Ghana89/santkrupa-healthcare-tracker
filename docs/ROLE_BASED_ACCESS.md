# Role-Based Access Control & Multi-Tenant Implementation

## Overview
The SantKrupa Healthcare Platform now implements a complete **role-based access control (RBAC)** system with multi-tenant architecture. Each role has specific access levels and capabilities.

---

## User Roles

### 1. **Super Admin**
- **Access Level:** Platform-wide
- **Permissions:**
  - Register new clinics
  - Access clinic registration form with full visibility
  - Manage platform-level settings
  
- **Homepage View:**
  - "Register New Clinic" option is prominently displayed
  - Can register multiple clinics

### 2. **Clinic Admin**
- **Access Level:** Clinic-specific
- **Permissions:**
  - Register new patients
  - Register doctors
  - Register receptionists
  - View all staff and patient data within their clinic
  - Access clinic admin dashboard
  - Manage clinic operations

- **Dashboard Features:**
  - Quick stats (Total Patients, Doctors, Receptionists, Prescriptions)
  - Patient Management panel
  - Staff Management panel
  - Analytics and Settings access
  - Admin Panel access

### 3. **Doctor**
- **Access Level:** Clinic-specific
- **Permissions:**
  - View assigned patients
  - Create prescriptions
  - Add medical notes
  - Manage patient care

### 4. **Receptionist**
- **Access Level:** Clinic-specific
- **Permissions:**
  - Register patients
  - Check-in patients
  - Manage appointment scheduling
  - Upload medical reports

### 5. **Patient**
- **Access Level:** Personal
- **Permissions:**
  - View own prescriptions
  - View own test reports
  - Download medical records
  - Upload personal medical reports

---

## Homepage Access Rules

### For Unauthenticated Users:
```
┌─────────────────────────────────────────┐
│   Existing User Login                   │  ← Standard login
├─────────────────────────────────────────┤
│   Clinic Admin Login / Register New...  │  ← Dynamic based on role
└─────────────────────────────────────────┘
```

### For Super Admin (when logged in):
```
┌─────────────────────────────────────────┐
│   Existing User Login                   │
├─────────────────────────────────────────┤
│   Register New Clinic (Full Access)     │  ← Super admin only
└─────────────────────────────────────────┘
```

### For Other Authenticated Users:
```
┌─────────────────────────────────────────┐
│   Existing User Login                   │
├─────────────────────────────────────────┤
│   Clinic Admin Login / Operations       │  ← Clinic-specific features
└─────────────────────────────────────────┘
```

---

## Clinic Admin Dashboard

When a clinic admin logs in, they see:

### Quick Stats Section
- Total Patients in clinic
- Total Doctors in clinic
- Total Receptionists in clinic
- Total Prescriptions in clinic

### Management Panels

#### Patient Management
- **Register New Patient** - Direct access to patient registration form
- **View All Patients** - Browse all registered patients in clinic

#### Staff Management
- **Add Doctor** - Create new doctor account with specialization
- **Add Receptionist** - Create new receptionist account
- **View All Doctors** - List all doctors in clinic
- **View All Receptionists** - List all reception staff

### Additional Features
- **Analytics** - View clinic statistics and metrics
- **Clinic Settings** - Manage clinic profile
- **Admin Panel** - Django admin access for advanced management

---

## Implementation Details

### Homepage Changes (`homepage.html`)

**Conditional Clinic Registration Button:**
```html
{% if user.is_authenticated and user.role == 'super_admin' %}
    <!-- Show "Register New Clinic" button -->
{% else %}
    <!-- Show "Clinic Admin Login" button -->
{% endif %}
```

**No Clinics Message:**
```html
{% if clinics %}
    <!-- Show clinics -->
{% else %}
    {% if user.is_authenticated and user.role == 'super_admin' %}
        <!-- Show "Register First Clinic" option -->
    {% endif %}
{% endif %}
```

### Admin Dashboard View (`views.py`)

**Clinic-Filtered Queries:**
```python
def admin_dashboard(request):
    clinic = getattr(request, 'clinic', None) or request.user.clinic
    total_patients = Patient.objects.filter(clinic=clinic).count()
    total_doctors = Doctor.objects.filter(clinic=clinic).count()
    # ... more filtered queries
```

### Admin Dashboard Template (`admin/dashboard.html`)

**Professional Bootstrap Layout:**
- Responsive card-based design
- Quick stats with icons
- Organized action panels
- Management shortcuts
- System summary table

---

## Security Features

### Multi-Tenant Isolation
- All queries are filtered by clinic
- Data from one clinic is invisible to another clinic's admins
- Role-based decorators prevent unauthorized access

### Access Control
- `@login_required` decorator on all admin views
- Role validation: `if request.user.role != 'admin': return redirect('homepage')`
- Clinic context enforcement via middleware

### Data Privacy
- Each clinic's data is completely isolated
- Only clinic members can access clinic data
- Super admins can manage all clinics but data remains isolated

---

## Workflow Examples

### Example 1: New Clinic Registration
1. Super Admin visits homepage
2. Clicks "Register New Clinic"
3. Fills clinic registration form
4. System auto-creates clinic admin account
5. Displays admin credentials (username & password)
6. Clinic admin can immediately login and manage their clinic

### Example 2: Clinic Admin Operations
1. Clinic Admin logs in via `/clinic/<slug>/login/`
2. Redirected to clinic admin dashboard
3. Can see all clinic statistics
4. Options to:
   - Register new patients
   - Add doctors
   - Add receptionists
   - View all staff and patients
   - Access analytics

### Example 3: Patient Registration by Reception
1. Receptionist logs into clinic
2. Navigates to patient registration (via admin or direct URL)
3. Registers new patient with details
4. Patient ID auto-generated per clinic
5. Patient receives login credentials
6. Patient can access own portal

---

## Database Architecture

### Multi-Tenant Data Model
```
Clinic (Root Tenant)
├── Users (clinic_id FK)
├── Patients (clinic_id FK)
├── Doctors (clinic_id FK)
├── Prescriptions (clinic_id FK)
├── Tests (clinic_id FK)
├── Medicines (clinic_id FK)
├── DoctorNotes (clinic_id FK)
├── MedicalReports (clinic_id FK)
├── PatientVisits (clinic_id FK)
└── TestReports (clinic_id FK)
```

All models include:
- `clinic = ForeignKey(Clinic, on_delete=models.CASCADE)`
- `objects = ClinicManager()` - Auto-filters by clinic context

---

## Testing the Implementation

### Test Case 1: Super Admin Access
1. Login with super_admin role
2. Verify "Register New Clinic" is visible on homepage
3. Register a new clinic
4. Confirm admin credentials are displayed
5. Try accessing with clinic admin credentials

### Test Case 2: Clinic Admin Dashboard
1. Login with clinic admin account
2. Verify correct clinic's statistics are shown
3. Click "Register New Patient"
4. Verify patient registration form appears
5. Create a patient and verify it's associated with correct clinic

### Test Case 3: Data Isolation
1. Create two clinics with different admins
2. Admin 1 registers patients in their clinic
3. Login as Admin 2
4. Verify you cannot see Admin 1's patients
5. All data remains isolated

---

## Files Modified

1. **`hospital/views.py`**
   - Updated `admin_dashboard` to filter by clinic
   - Added clinic context to queries

2. **`hospital/templates/hospital/homepage.html`**
   - Added conditional rendering for "Register Clinic" option
   - Super admin only shows registration form
   - Others see clinic admin login option

3. **`hospital/templates/hospital/admin/dashboard.html`**
   - Complete Bootstrap redesign
   - Added patient management panel
   - Added staff management panel
   - Responsive layout with stats

4. **`hospital/templates/hospital/base.html`**
   - Integrated Bootstrap 5
   - Added Font Awesome icons
   - Improved navbar with role badges
   - Better message display

---

## Next Steps

- [ ] Implement analytics dashboard for clinic admins
- [ ] Add clinic settings/profile management
- [ ] Implement audit logging for all operations
- [ ] Add email notifications for new accounts
- [ ] Create clinic subscription management
- [ ] Implement data export features
- [ ] Add advanced reporting

---

## Support & Documentation

For more information about the multi-tenant architecture, see:
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `COMPLETE_SETUP_GUIDE.md` - Setup instructions
- `DATABASE_SCHEMA.md` - Database structure

