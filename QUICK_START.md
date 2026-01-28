# 🏥 QUICK REFERENCE GUIDE

## 🚀 START HERE

### Run the Server
```powershell
cd c:\Users\ADMIN\Documents\healthcare\santkrupa-healthcare-tracker
.venv\Scripts\Activate.ps1
python manage.py runserver
```

Access: http://localhost:8000/

---

## 👨‍💼 Admin Access

**URL:** http://localhost:8000/admin/  
**Username:** admin  
**Password:** admin123  

### First Steps as Admin
1. Go to Admin Dashboard: http://localhost:8000/admin-dashboard/
2. Create a Doctor Account: http://localhost:8000/admin-dashboard/create-doctor/
3. Create a Receptionist Account: http://localhost:8000/admin-dashboard/create-receptionist/
4. Test the system

---

## 👤 For Reception Staff

**URL:** http://localhost:8000/reception/dashboard/

### Register Patient
1. Click "Register Patient"
2. Enter: Name, Age, Address, Phone
3. System auto-generates: Patient ID, Password
4. Share credentials with patient

**Example Output:**
```
Patient ID: PT202600234
Password: aBc123Def
```

---

## ⚕️ For Doctor

**URL:** http://localhost:8000/doctor/dashboard/

### Create Prescription
1. Select a patient
2. Click "Create Prescription"
3. Add Tests (blood, ultrasound, x-ray, etc.)
4. Add Medicines (dosage, frequency, duration)
5. Record Doctor's Notes (observations, diagnosis, plan)
6. Complete Prescription

---

## 💳 For Patient

**URL:** http://localhost:8000/patient/dashboard/

### Login
```
Username: Your Patient ID (e.g., PT202600234)
Password: Your auto-generated password
```

### View Health Data
1. See all prescriptions
2. View prescribed tests
3. Read medicines
4. Upload medical reports

---

## 🔗 ALL URLS

| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/admin/` | Django admin |
| `/admin-dashboard/` | Admin dashboard |
| `/admin-dashboard/create-doctor/` | Create doctor account |
| `/admin-dashboard/create-receptionist/` | Create receptionist account |
| `/reception/dashboard/` | Reception dashboard |
| `/reception/register-patient/` | Register patient |
| `/doctor/dashboard/` | Doctor dashboard |
| `/patient/dashboard/` | Patient dashboard |

---

## 📊 Database

**File:** `db.sqlite3`  
**Already Migrated:** ✅ Yes  
**Tables Created:** ✅ 8 models  

---

## 🔐 Password Reset

If you forget admin password, delete `db.sqlite3` and run:
```powershell
python manage.py migrate
python setup_admin.py
```

New admin credentials:
```
Username: admin
Password: admin123
```

---

## 📱 Features Summary

| Feature | Who Uses | Status |
|---------|----------|--------|
| Register Patients | Reception | ✅ Ready |
| Create Prescriptions | Doctor | ✅ Ready |
| Add Tests | Doctor | ✅ Ready |
| Add Medicines | Doctor | ✅ Ready |
| Record Notes | Doctor | ✅ Ready |
| View Prescriptions | Patient | ✅ Ready |
| Upload Reports | Patient | ✅ Ready |
| Manage Users | Admin | ✅ Ready |

---

## 🆘 Troubleshooting

### Server Won't Start
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run server
python manage.py runserver
```

### Port 8000 Already in Use
```powershell
python manage.py runserver 8001
```

### Database Error
```powershell
python manage.py migrate
```

---

## 📚 Documentation

- **WORKFLOW.md** - Complete workflow guide
- **COMPLETE_SETUP_GUIDE.md** - Detailed setup
- **DATABASE_SCHEMA.md** - Database structure
- **IMPLEMENTATION_SUMMARY.md** - What was done

---

## 🎯 Test Workflow

### 1. Create Receptionist
1. Login as admin at `/admin-dashboard/`
2. Click "Create Receptionist"
3. Create account with username: `reception1`

### 2. Register Test Patient
1. Login as receptionist
2. Go to `/reception/dashboard/`
3. Register patient: John Doe, 35 years old
4. Get Patient ID and Password

### 3. Create Doctor
1. Login as admin
2. Click "Create Doctor"
3. Create account: username `doctor1`, specialization: Cardiology

### 4. Create Prescription
1. Login as doctor
2. Go to `/doctor/dashboard/`
3. Select John Doe patient
4. Create prescription with tests and medicines
5. Complete it

### 5. View as Patient
1. Login with Patient ID and password
2. Go to `/patient/dashboard/`
3. See all prescription details

---

## ⚡ Key Shortcuts

| Action | Command |
|--------|---------|
| Restart Server | Ctrl+C, then `python manage.py runserver` |
| Reset Database | Delete `db.sqlite3`, run `migrate`, run `setup_admin.py` |
| View Admin Panel | http://localhost:8000/admin/ |
| Create User | Go to Admin Dashboard |
| View Patients | http://localhost:8000/reception/dashboard/ |

---

## 📞 Support

For questions about:
- **Workflow:** See WORKFLOW.md
- **Database:** See DATABASE_SCHEMA.md
- **Setup:** See COMPLETE_SETUP_GUIDE.md
- **Errors:** Check terminal output

---

## ✅ Checklist

- [ ] Server is running
- [ ] Admin account works
- [ ] Create doctor account
- [ ] Create receptionist account
- [ ] Register a test patient
- [ ] Doctor creates prescription
- [ ] Patient views data
- [ ] System working correctly

---

**System Status:** ✅ OPERATIONAL  
**Ready to Use:** ✅ YES  
**Documentation:** ✅ COMPLETE  

Start at: http://localhost:8000/
