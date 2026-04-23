# 🧪 Quick Testing Guide

## Prerequisites
- Django development server running: `python manage.py runserver`
- You're logged in as: Doctor, Receptionist, or Admin
- You have test data (patients, prescriptions)

---

## Test 1: Medicine Types (Soap & Lotion)

### Test Steps:
```
1. Go to Doctor Console → Prescriptions → Create New
2. Fill in: Patient, Doctor, Date
3. In "Add Medicine" section:
   - Medicine: Select any medicine
   - Type: Select "Soap" from dropdown
   - Dosage: "5% solution"
   - Schedule: "Once daily"
   - Duration: "7 days"
   - Click "Add"
4. Add another medicine with type "Lotion"
5. Click "Save Prescription"
6. Click "Print Preview"
7. Verify both medicines appear with their types in the printout
```

### Expected Result:
✅ Both Soap and Lotion types appear in dropdown and in prescription printout

---

## Test 2: Patient Registration Edit

### Test Steps:
```
1. Go to Reception → Patient Management
2. Find a patient and click to view details
3. Look for "✏️ Edit Patient" button (green button at top)
4. Click the Edit button
5. You should see the edit form with fields:
   - Patient ID (read-only)
   - Status (read-only)
   - Name, Gender, DOB, Weight
   - Age (auto-calculates from DOB)
   - Phone, Address
6. Change the phone number to something else (e.g., "9999999999")
7. Click "Save Changes" button
8. You should see success message
9. Go back to patient details to verify change was saved
```

### Expected Result:
✅ Edit form appears → Changes save → Patient details updated

---

## Test 3: Download Prescription as PDF

### Test Steps:
```
1. Go to Doctor Console → Prescriptions
2. Find a prescription with medicines already added
3. Click "Print Preview" or "View" button
4. Look for green button at top: "📥 Download PDF"
5. Click "Download PDF"
6. You should see: "⏳ Generating PDF..." (loading state)
7. Browser downloads file: prescription_[ID]_[PatientName].pdf
8. Open the downloaded PDF
9. Verify it looks exactly like the print preview
   - Same layout, colors, fonts
   - All patient info is present
   - All medicines are listed
   - All tests are listed
```

### Expected Result:
✅ PDF downloads → Opens in viewer → Matches print layout exactly

---

## Test 4: Share via WhatsApp

### Test Steps:
```
1. View a prescription (same as Test 3)
2. Look for button: "📱 Share WhatsApp"
3. Click the button
4. WhatsApp should open with pre-filled message like:
   ---
   Rx Prescription
   Patient: [Name] (ID: [ID])
   Doctor: Dr. [Name]
   Date: [Date]
   
   💊 Medicines:
   - [Medicine] - [Dosage] - [Schedule] - [Duration]
   
   🧪 Tests:
   - [Test names]
   
   Notes: [Any doctor notes]
   ---
5. Choose a contact or leave to send to yourself for testing
6. Send the message
7. Verify message arrives and is readable
```

### Expected Result:
✅ WhatsApp opens → Message is pre-filled → Message can be sent

**Note:** If WhatsApp Web works better for you, use that instead of mobile app.

---

## Test 5: Share via SMS

### Test Steps:
```
1. View a prescription (same as Test 3)
2. Look for button: "💬 Share SMS"
3. Click the button
4. SMS app should open with message like:
   ---
   Rx: [Patient Name]
   Dr: [Doctor]
   Meds: [Med1], [Med2], [Med3]
   Tests: [Test1], [Test2]
   Date: [Date]
   ID: [Prescription ID]
   ---
5. Choose a recipient (use test number or your own)
6. Send the message
7. Verify message is delivered
```

### Expected Result:
✅ SMS app opens → Message is pre-filled → Can be sent

---

## Common Issues & Solutions

### ❌ "File is not downloading"
**Solution:**
- Check browser's download folder
- Look at browser console (F12 → Console)
- Try a different browser
- Reload page and try again

### ❌ "pdf download works but doesn't match print"
**Solution:**
- The html2pdf.js library takes a screenshot of HTML
- If layout looks different, it's a CSS printing issue
- Try adjusting print preview size (A4, A5) first
- Then try PDF download again

### ❌ "Edit Patient button not appearing"
**Solution:**
- Make sure you're logged in as Receptionist or Admin
- Go to Reception section, not Doctor section
- Try refreshing the page

### ❌ "WhatsApp/SMS not opening"
**Solution:**
- Mobile: Make sure app is installed
- Desktop: Try WhatsApp Web (web.whatsapp.com)
- Check browser console for errors

### ❌ "Medicine types (Soap/Lotion) not showing in dropdown"
**Solution:**
- Refresh the page
- Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Restart Django server

---

## Information That Should Display

### In Patient Edit Form:
```
Read-Only Fields:
- Patient ID: PATIENTS_YYYY_001 (example)
- Registration Date: 01-01-2024
- Status: Active

Editable Fields:
- Name: [Current name]
- Gender: Male/Female/Other
- Date of Birth: [Auto-calculates age]
- Weight: [kg]
- Age: [Auto-filled from DOB]
- Phone: [10-digit number]
- Address: [Current address]
```

### In Prescription Download Message:
```
PDF Filename: prescription_[ID]_[Patient_Name].pdf
PDF Format: A4 portrait, same as print preview
PDF Quality: High-resolution (2x scale)
```

### In WhatsApp Share Message:
```
Patient Name and ID ✓
Doctor Name ✓
Date ✓
All Medicines Listed ✓
All Tests Listed ✓
Doctor Notes (if any) ✓
```

### In SMS Share Message:
```
Patient Name ✓
Doctor Name ✓
Key Medicines (first 3) ✓
Tests (first 3) ✓
Prescription ID ✓
```

---

## Success Criteria Checklist

- [ ] Medicine types accept "Soap" and "Lotion"
- [ ] Edit button appears in patient details
- [ ] Can edit patient information
- [ ] PDF downloads match print layout
- [ ] WhatsApp message is pre-filled
- [ ] SMS message is pre-filled
- [ ] All buttons are clickable (not broken)
- [ ] No JavaScript errors in console
- [ ] Multi-clinic access works (if applicable)

---

## Troubleshooting Command

If something is not working, run this in terminal:
```bash
python manage.py shell

# Check if medicine types exist
from hospital.models import MasterMedicine
print(MasterMedicine._meta.get_field('medicine_type').choices)

# Should print all types including ('soap', 'Soap') and ('lotion', 'Lotion')
```

---

## Performance Notes

- **PDF Generation:** ~1-3 seconds (client-side in browser)
- **WhatsApp/SMS:** Instant (just opens app with message)
- **Edit Patient:** ~500ms (form submission)
- **Page Load:** ~1-2 seconds (all resources cached after first load)

---

## Browser Compatibility

**Works on:**
- ✅ Chrome/Chromium (100%+)
- ✅ Firefox (95%+)
- ✅ Safari (95%+)
- ✅ Edge (98%+)

**Mobile:**
- ✅ iOS Safari
- ✅ Android Chrome
- ✅ Android Firefox

---

## Next: Deploying to Production

Once all tests pass, to deploy:

1. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Run database check:**
   ```bash
   python manage.py check --deploy
   ```

3. **Verify all tests pass:**
   ```bash
   python manage.py test hospital
   ```

4. **Deploy to server** (Gunicorn, etc.)
   - Features require no special server setup
   - Just ensure Django is running
   - pdf Download works entirely client-side

---

**Need Help?** Check the detailed documentation in `FEATURES_IMPLEMENTED.md`

