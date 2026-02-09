# Multi-Tenant Migration Readiness Guide

## Overview
This guide walks through preparing and executing the database migrations for the multi-tenant healthcare system.

## Pre-Migration Checklist

### 1. Code Changes Verification ✅
- [x] `hospital/managers.py` created with ClinicManager
- [x] `hospital/middleware.py` created with TenantMiddleware
- [x] `hospital/models.py` updated with Clinic model and clinic_id fields on all models
- [x] `santkrupa_hospital/settings.py` updated with TenantMiddleware registration
- [x] `santkrupa_hospital/urls.py` refactored for multi-tenant routing
- [x] All syntax validated (no Python errors)

### 2. Environment Prerequisites
- [x] Python 3.9+ installed
- [x] Django 4.2+ installed
- [x] All dependencies in requirements.txt available
- [x] Virtual environment activated

### 3. Backup Strategy
**Before running migrations:**
```bash
# Backup current database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Or for PostgreSQL:
# pg_dump santkrupa_hospital > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Migration Steps

### Step 1: Create Migrations

```bash
# Generate migration files based on model changes
python manage.py makemigrations
```

**Expected Output:**
```
Migrations for 'hospital':
  hospital/migrations/0003_clinic.py
    - Create model Clinic
  hospital/migrations/0004_user_clinic.py
    - Add field clinic to user
  hospital/migrations/0005_alter_user_options.py
    - Alter unique_together for User
  ... (additional migrations for each model update)
```

**What Happens:**
- Django analyzes current models vs. existing migrations
- Creates new migration files in `hospital/migrations/`
- One migration file per logical group of changes
- Each migration is numbered sequentially

### Step 2: Review Migrations

```bash
# List all migrations
python manage.py showmigrations hospital

# Expected output:
# hospital
#  [ ] 0001_initial
#  [ ] 0002_patientvisit_testreport
#  [ ] 0003_clinic
#  [ ] 0004_user_clinic
#  ...
```

```bash
# Review specific migration SQL
python manage.py sqlmigrate hospital 0003_clinic

# Review complete migration changes
python manage.py sqlmigrate hospital 0003_clinic 0004_user_clinic 0005_alter_user_options
```

**What to Check:**
- Verify CREATE TABLE statements for new Clinic model
- Verify ALTER TABLE statements adding clinic_id to existing models
- Verify UNIQUE constraints are added correctly
- Verify indexes are created (if specified in model Meta)
- Verify no DROP TABLE or dangerous operations

### Step 3: Test Migrations (Development)

```bash
# Apply migrations to development database
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, hospital
# Running migrations:
#   Applying hospital.0003_clinic... OK
#   Applying hospital.0004_user_clinic... OK
#   ...
```

**What Happens:**
- Creates Clinic table with all fields
- Adds clinic_id columns to existing models
- Creates indexes and constraints
- Updates Django's internal migration tracking

### Step 4: Verify Schema

```bash
# Connect to database and verify
sqlite3 db.sqlite3

# List all tables
.tables

# Verify clinic table structure
.schema hospital_clinic

# Expected output:
# CREATE TABLE hospital_clinic (
#     id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
#     name varchar(255) NOT NULL UNIQUE,
#     slug varchar(50) NOT NULL UNIQUE,
#     ...
# );

# Verify clinic_id added to other models
.schema hospital_patient

# Should include:
# clinic_id integer NOT NULL REFERENCES hospital_clinic (id) DEFERRABLE INITIALLY DEFERRED,
```

### Step 5: Create Initial Clinic (Seed Data)

```bash
# Open Django shell
python manage.py shell
```

```python
from hospital.models import Clinic
from django.utils.text import slugify

# Create initial clinic (if converting from single-tenant)
clinic = Clinic.objects.create(
    name='Santkrupa Hospital',
    slug='santkrupa',
    address='123 Medical St',
    city='Bangalore',
    state='Karnataka',
    zip_code='560001',
    phone_number='+91-80-XXXX-XXXX',
    email='admin@santkrupa.com',
    website='https://santkrupa.com',
    registration_number='REG-2024-001',
    subscription_status='active',
    max_doctors=50,
    max_patients=1000,
    max_receptionists=10,
    is_active=True
)

print(f"Created clinic: {clinic.name} (slug: {clinic.slug})")

# Exit shell
exit()
```

### Step 6: Migrate Existing Data (If Applicable)

**For upgrading from single-tenant to multi-tenant:**

```python
# Django shell script to assign existing users to clinic
python manage.py shell
```

```python
from hospital.models import Clinic, User, Patient, Doctor

# Get or create the default clinic
clinic, created = Clinic.objects.get_or_create(
    slug='santkrupa',
    defaults={
        'name': 'Santkrupa Hospital',
        'address': '123 Medical St',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'zip_code': '560001',
        'phone_number': '+91-80-XXXX-XXXX',
        'email': 'admin@santkrupa.com',
        'registration_number': 'REG-2024-001'
    }
)

print(f"Using clinic: {clinic.name}")

# Update all existing users to belong to clinic
User.objects.filter(clinic__isnull=True).update(clinic=clinic)
users_updated = User.objects.filter(clinic=clinic).count()
print(f"Updated {users_updated} users to clinic: {clinic.slug}")

# Update all existing patients to belong to clinic
Patient.objects.filter(clinic__isnull=True).update(clinic=clinic)
patients_updated = Patient.objects.filter(clinic=clinic).count()
print(f"Updated {patients_updated} patients to clinic: {clinic.slug}")

# Update all existing doctors
Doctor.objects.filter(clinic__isnull=True).update(clinic=clinic)
doctors_updated = Doctor.objects.filter(clinic=clinic).count()
print(f"Updated {doctors_updated} doctors to clinic: {clinic.slug}")

# Update all other related models similarly
# ... (prescription, test, medicine, etc.)

print("\nData migration completed!")
```

## Post-Migration Verification

### 1. Test Admin Interface

```bash
# Start development server
python manage.py runserver
```

- Navigate to: http://localhost:8000/admin/
- Login with superuser credentials
- Verify Clinic model appears in admin
- Verify clinic_id appears on all models
- Create a test clinic through admin

### 2. Test Multi-Tenant Isolation

```python
# Django shell test
python manage.py shell
```

```python
from hospital.models import Clinic, User, Patient, get_current_clinic, set_current_clinic

# Test 1: Create multiple clinics
clinic1 = Clinic.objects.create(
    name='Clinic One',
    slug='clinic-one',
    # ... other fields
)

clinic2 = Clinic.objects.create(
    name='Clinic Two',
    slug='clinic-two',
    # ... other fields
)

print(f"Created: {clinic1.name}, {clinic2.name}")

# Test 2: Create patients in different clinics
user1 = User.objects.create_user(
    username='user1',
    password='test123',
    clinic=clinic1,
    role='patient'
)

user2 = User.objects.create_user(
    username='user2',
    password='test123',
    clinic=clinic2,
    role='patient'
)

patient1 = Patient.objects.create(
    clinic=clinic1,
    patient_name='John Doe',
    # ... other fields
)

patient2 = Patient.objects.create(
    clinic=clinic2,
    patient_name='Jane Smith',
    # ... other fields
)

# Test 3: Test isolation with context
set_current_clinic(clinic1)
clinic1_patients = Patient.objects.all()
print(f"Clinic1 patients: {clinic1_patients.count()}")

set_current_clinic(clinic2)
clinic2_patients = Patient.objects.all()
print(f"Clinic2 patients: {clinic2_patients.count()}")

print("✅ Isolation test passed!")
```

### 3. Test URL Routing

```bash
# Test clinic-specific URLs
# Navigate to: http://localhost:8000/clinic/santkrupa/patient/dashboard/
# Should display patient dashboard for Santkrupa clinic

# Navigate to: http://localhost:8000/clinic/clinic-one/patient/dashboard/
# Should display patient dashboard for Clinic One

# Test that data is properly isolated per clinic URL
```

### 4. Test Context Management

```python
# In a Django view or middleware test
from hospital.middleware import TenantMiddleware, get_current_clinic, set_current_clinic

# Simulate request processing
set_current_clinic(clinic1)
current = get_current_clinic()
assert current.id == clinic1.id
print("✅ Context management working")
```

## Rollback Procedure

**If migration fails or issues occur:**

```bash
# Rollback last migration
python manage.py migrate hospital 0002

# Rollback all migrations for hospital app
python manage.py migrate hospital zero

# Restore from backup
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3
```

## Production Migration Checklist

### Before Migration to Production:

- [ ] Full database backup taken
- [ ] Backup verified restorable
- [ ] Downtime window scheduled
- [ ] Team notified
- [ ] Rollback procedure tested
- [ ] All code changes deployed

### During Migration:

- [ ] Place application in maintenance mode
- [ ] Run: `python manage.py migrate`
- [ ] Monitor migration progress
- [ ] Verify no errors in logs
- [ ] Run post-migration verification

### After Migration:

- [ ] Verify data integrity
- [ ] Test key functionality
- [ ] Monitor error logs
- [ ] Remove maintenance mode
- [ ] Communicate completion to team

## Common Migration Issues & Solutions

### Issue 1: "Column Already Exists"
**Cause:** Migration already applied or previous failed migration
**Solution:**
```bash
python manage.py migrate --fake-initial
python manage.py showmigrations  # Check status
```

### Issue 2: "NOT NULL Constraint Failed"
**Cause:** Adding NOT NULL field to table with existing rows
**Solution:** Use null=True initially, then migrate data, then alter to NOT NULL

### Issue 3: "Unique Constraint Violation"
**Cause:** unique_together constraint conflicts with existing data
**Solution:**
```python
# Remove duplicates or migrate data before applying constraint
# Then create migration with constraint
```

### Issue 4: Foreign Key Relationship Error
**Cause:** Clinic model not created before referenced by other models
**Solution:** Migrations are ordered sequentially; ensure clinic is created first

## Migration Timeline Estimate

| Step | Time | Notes |
|------|------|-------|
| Backup | 2 min | Always first! |
| makemigrations | 1 min | Generate migrations |
| Review SQL | 5 min | Critical validation |
| Run migrate | 5-10 min | Depends on data volume |
| Seed initial clinic | 2 min | Create default clinic |
| Data migration | 10-30 min | Assigning existing data to clinic |
| Verification | 10 min | Test isolation & functionality |
| Rollback prep | 5 min | Just in case |
| **Total** | **40-60 min** | Small database; larger may take longer |

## Database Size Recommendations

- **Development:** SQLite (current)
- **Production:** PostgreSQL 13+ (recommended)
- **Reason:** Multi-tenancy + scalability requires mature RDBMS

To migrate to PostgreSQL:
```bash
# See DATABASE_SCHEMA.md section "PostgreSQL Setup" for detailed steps
```

---

**Migration Status:** Ready for execution ✅
**Next Action:** Run `python manage.py makemigrations` when ready to proceed
