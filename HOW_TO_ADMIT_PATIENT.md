# HOW TO ADMIT A PATIENT - STEP BY STEP GUIDE

## Overview
Doctors can now recommend and admit patients to the hospital with full treatment tracking. The system guides doctors through the admission process step-by-step.

---

## COMPLETE WORKFLOW

### STEP 1: Create a Prescription
**Location**: Doctor Dashboard → "All Patients" section
**Action**: 
- Find the patient in the "All Patients" list
- Click **"Create Prescription"** button
- System will create a new prescription for the patient

**Result**: You'll be redirected to the prescription details page

---

### STEP 2: Add Tests & Medicines
**Location**: Prescription Details Page
**Action**:
- Add required **tests** (blood test, X-ray, etc.)
- Add required **medicines** (with dosage, frequency, duration)
- Add **doctor notes** (observations, diagnosis, treatment plan)
- The autocomplete will suggest from your clinic's master templates

**Tips**:
- Type medicine/test name to see suggestions
- Select from dropdown to auto-populate details
- Fields auto-fill with default frequency and duration from templates

**Result**: All tests and medicines are now linked to this prescription

---

### STEP 3: Recommend Admission ⭐ (NEW)
**Location**: Prescription Details Page → "Recommend Admission?" section
**When to Use**: If patient needs hospital admission for monitoring or intensive treatment

**Action**:
- Scroll to the **yellow "Recommend Admission?" card**
- Enter the **reason for admission** (e.g., "Severe fever, needs IV fluids and monitoring")
- Click **"Recommend Admission"** button

**Result**: 
- Recommendation is saved
- You'll see a green "Admission Recommended" card
- **"Proceed to Admit Patient"** button appears

---

### STEP 4: Admit Patient to Hospital
**Location**: Prescription Details Page → "Admission Recommended" section
**Action**:
1. Click **"Proceed to Admit Patient"** button
2. Fill in the admission form:
   - **Admission Type**: General Ward, ICU, Emergency, Day Care, or Isolation
   - **Bed Number**: e.g., "ICU-5" or "Ward-A-12"
   - **Room Number**: e.g., "205" or "301"
   - **Reason for Admission**: (already filled from recommendation)
   - **Medical History**: Past conditions, chronic diseases
   - **Allergies** ⚠️: **CRITICAL** - Drug allergies, food allergies

3. Click **"Admit Patient"** button

**Result**: Patient is now admitted! You're taken to the Admission Details page

---

### STEP 5: Add Treatments During Admission
**Location**: Admission Details Page
**What Can You Track**:

#### A) **Medications**
- Medicine name, dosage, frequency, route (Oral/IV/IM/etc.)
- Duration of medication

#### B) **Injections**
- Injection name, dosage, route
- When given and patient response

#### C) **Saline/IV Fluids** 💧
- Type: Normal Saline, D5W, Ringer's Lactate, etc.
- Quantity: 500ml, 1L, etc.
- When started

#### D) **Oxygen Therapy** 💨
- Type: Nasal Cannula, Face Mask, Ventilator, CPAP
- Flow rate: 2L/min, 40%, etc.
- Duration

#### E) **Procedures/Surgeries**
- Procedure name
- Duration
- Notes about the procedure

#### F) **Monitoring**
- Vital signs records
- Observations

**Action**:
1. From Admission Details page, click **"+ Add Treatment"** button
2. Select treatment type from dropdown
3. Fill in relevant fields (they change based on type selected)
4. Add notes about patient response
5. Click **"Save Treatment"**

**Result**: Treatment is logged with timestamp and doctor info

---

### STEP 6: Update Patient Status
**Location**: Admission Details Page → Status card (right sidebar)
**Options**:
- **Admitted** → Initial status when admitted
- **In Treatment** → Patient is receiving active treatment
- **Improving** → Patient showing improvement
- **Stable** → Patient condition is stable
- **Ready for Discharge** → Patient ready to go home
- **Discharged** → Patient has been discharged
- **Shifted** → Transferred to another facility
- **Deceased** → Sadly, patient passed away

**Action**:
1. Select new status from dropdown
2. If selecting "Discharged":
   - Add **Discharge Notes**
   - Set **Follow-up Date** (when patient should return)
   - Add **Follow-up Instructions** (medications to continue, diet, etc.)
3. Click **"Update Status"**

**Result**: Status updated and patient can be discharged

---

## QUICK ACCESS POINTS

### From Doctor Dashboard:
- **📋 Pending Prescriptions** - See all active prescriptions
- **🏥 Admission Needed** - See patients recommended for admission
- **Admissions Dashboard** (green button) - View all current hospital admissions
- **"How to Admit Patient"** - Step-by-step guide (on dashboard)

### From Patient Details:
- **Create Prescription** - Start a new prescription
- **View History** - See all previous prescriptions and admissions
- **View Admissions** - All past and current admissions

### Admission Recommendations Page:
- **URL**: `/clinic/<clinic_slug>/doctor/admission-recommendations/`
- View all patients you've recommended for admission
- Filter by "Pending Admission" or "Already Admitted"
- Quick links to admit or view current admission

---

## KEY INFORMATION STORED

### For Each Admission:
✓ Patient info (name, ID, age, contact)
✓ Doctor assigned
✓ Admission date & time
✓ Admission type (ward/ICU/emergency)
✓ Bed & room assignment
✓ Reason for admission
✓ Medical history
✓ **Allergies** (prominently displayed in red)
✓ Current status
✓ All treatments given (with timestamp)
✓ Discharge date & notes (if discharged)
✓ Follow-up date & instructions

### For Each Treatment:
✓ Type of treatment
✓ Medicine/procedure name
✓ Dosage & frequency (if applicable)
✓ Route of administration
✓ When given (exact date/time)
✓ Duration
✓ Doctor who administered
✓ Notes & observations

---

## SEARCH & FILTER

### Find Patients by Name or ID
- **Admissions Dashboard**: Search box at top
- **Admission Recommendations**: Filter by status (Pending/Admitted)

### View Patient Admission History
- Patient Details page → **"View Admissions"** button
- Shows all past and current admissions with details

---

## IMPORTANT FEATURES

### ⚠️ Allergies Alert
- Prominently displayed in RED box in admission details
- Critical for patient safety
- Always review before giving any medication

### 📊 Statistics Dashboard
- Total patients currently admitted
- ICU occupancy
- General ward occupancy
- Emergency cases

### 📅 Duration Tracking
- Auto-calculates how many days patient has been admitted
- Visible on admission details

### 🔗 Treatment Log Search
- All treatments logged chronologically
- See exact time each treatment was given
- Doctor name and observations recorded

---

## TYPICAL SCENARIO EXAMPLES

### Example 1: High Fever Patient
1. Create prescription with fever-related tests
2. Add antibiotics and IV fluid prescription
3. **Recommend Admission** → "High fever, needs IV fluids and monitoring"
4. **Admit to General Ward**
5. **Add treatments**: 
   - Antibiotic injection (8-hourly)
   - Saline IV (Normal Saline 500ml, 6-hourly)
   - Paracetamol tablet (As needed for fever)
6. Monitor status → Update to "Stable" when fever subsides
7. After 48 hours stable → **Discharge** with follow-up in 3 days

### Example 2: Post-Surgery Patient
1. Create prescription for post-op care
2. Add pain management medicines, antibiotics
3. **Recommend Admission** → "Post-surgical monitoring required"
4. **Admit to General Ward**
5. **Add treatments**:
   - Pain relief injection (6-hourly)
   - Antibiotics (8-hourly)
   - IV fluids (Ringer's Lactate)
   - Wound care observations
6. Update status as patient recovers
7. **Discharge** with wound care instructions

### Example 3: ICU Critical Patient
1. Create prescription with emergency status
2. Add critical medications
3. **Recommend Admission** → "Critical condition requires ICU care"
4. **Admit to ICU**
5. **Add treatments**:
   - Multiple medications hourly
   - Oxygen therapy (High flow)
   - IV fluids and blood transfusion
   - Continuous monitoring notes
6. Update status as patient improves
7. If improving → Transfer to general ward → Discharge
8. Or → Document incident if patient passed away

---

## TROUBLESHOOTING

### Can't see "Recommend Admission" button?
→ Make sure you're logged in as a doctor
→ Make sure you're on the prescription details page
→ If already recommended, it will show "Admission Recommended" instead

### Can't find patient to admit?
→ Use search box in doctor dashboard
→ Or go to Reception Dashboard → Search patient
→ Check if patient is already admitted (won't show in "Create Prescription")

### Can't add treatment?
→ Make sure patient is admitted first
→ Make sure you're on the Admission Details page
→ Click the "Add Treatment" button

### Don't see admission recommendation?
→ Go to Doctor Dashboard → "Admission Needed" card
→ Or visit: `/clinic/<slug>/doctor/admission-recommendations/`

---

## TIPS & BEST PRACTICES

✅ **Always fill allergies** when admitting patient
✅ **Add observations** after each treatment for better tracking
✅ **Update status regularly** so team knows patient condition
✅ **Use specific dosages** from master templates
✅ **Record follow-up instructions** when discharging
✅ **Review medical history** before prescribing
✅ **Check allergy alerts** prominently displayed
✅ **Use timestamps** to track treatment progression

---

## FEATURES RECAP

| Feature | Where to Find | Who Can Use |
|---------|--------------|-----------|
| Recommend Admission | Prescription Details | Doctor |
| Admit Patient | Admit Patient Form | Doctor |
| View Admissions | Admissions Dashboard | Doctor, Admin |
| Add Treatments | Admission Details | Doctor |
| Update Status | Admission Details | Doctor, Admin |
| Track History | Patient Admissions | Doctor, Admin |
| Upload Medical Reports | Patient Dashboard | Patient |

---

## DATABASE INFORMATION

**New Models Created**:
- `PatientAdmission` - Stores admission records
- `TreatmentLog` - Stores all treatments given

**Updated Models**:
- `Prescription` - Added `admission_recommended` and `admission_reason` fields

**Migration Applied**: `0006_prescription_admission_reason_and_more.py`
