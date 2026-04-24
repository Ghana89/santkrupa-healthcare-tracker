# IST Timezone Configuration - Deployment Verification Checklist

## Pre-Deployment Checklist

### Settings Configuration
- [ ] `TIME_ZONE = 'Asia/Kolkata'` in `settings.py`
- [ ] `LANGUAGE_CODE = 'en-in'` in `settings.py`
- [ ] `USE_TZ = True` in `settings.py`
- [ ] All three settings verified in Django shell

### Code Changes
- [ ] `custom_filters.py` has three new filter functions
- [ ] Filters compile without syntax errors
- [ ] `views.py` has timezone conversion in AJAX endpoint
- [ ] Dashboard template loads `{% load custom_filters %}`

### Database
- [ ] No migrations needed (only settings changed)
- [ ] Existing datetime records still accessible
- [ ] Database remains unchanged

## Testing Checklist

### Setting Verification
```bash
python manage.py shell
```
- [ ] `from django.conf import settings`
- [ ] `settings.TIME_ZONE` shows `'Asia/Kolkata'`
- [ ] `settings.USE_TZ` is `True`
- [ ] `settings.LANGUAGE_CODE` is `'en-in'`

### Template Filter Testing
```django
{% load custom_filters %}
```
- [ ] Template loads without error
- [ ] `{{ now|format_ist_datetime }}` renders correctly
- [ ] `{{ now|format_ist_date }}` renders correctly
- [ ] `{{ now|format_ist_time }}` renders correctly

### Display Testing

**Check 1: Doctor Dashboard**
1. Navigate to `/clinic/santkrupa/doctor/dashboard/`
2. Look at "Today's Check-ins" section
3. - [ ] Check-in time shows as `HH:MM AM/PM` format
4. - [ ] Time matches IST (UTC+5:30 from actual time)

**Check 2: Prescriptions via AJAX**
1. Stay on doctor dashboard
2. Prescriptions table should populate
3. - [ ] Dates show as `DD MMM YYYY, HH:MM AM/PM`
4. - [ ] Times are in IST
5. Try search/filter
6. - [ ] Dates still show IST after filtering

**Check 3: Network Response**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click search on prescriptions
4. Find `/doctor/dashboard/prescriptions-ajax/` request
5. Check Response tab:
   ```json
   {
     "prescriptions": [{
       "date": "23 Apr 2026, 02:30 PM"
     }]
   }
   ```
6. - [ ] Dates are IST formatted in JSON

**Check 4: Time Accuracy**
1. Check system clock
2. Compare with displayed times on dashboard
3. - [ ] Displayed times are +5:30 hours from UTC
4. - [ ] Displayed times match IST

**Check 5: Multiple Times**
1. Refresh page at different times (e.g., 3:00 PM IST)
2. - [ ] Displayed times update correctly
3. - [ ] No timezone caching issues

### Cross-Browser Testing
- [ ] Chrome: Times show in IST
- [ ] Firefox: Times show in IST
- [ ] Safari: Times show in IST
- [ ] Edge: Times show in IST
- [ ] Mobile browsers: Times show in IST

### Mobile Testing
- [ ] Dashboard responsive on mobile
- [ ] Times visible and readable
- [ ] Check-in times in IST
- [ ] AJAX loads correctly on mobile

## Functional Testing

### Task 1: Create New Record
1. Create a new prescription
2. - [ ] Timestamp automatically uses current IST time
3. View the prescription
4. - [ ] Shows IST time when retrieved

### Task 2: Search by Date
1. Search for prescriptions from today
2. - [ ] Returns correct results based on IST date
3. Search for past dates
4. - [ ] Filters work correctly with IST dates

### Task 3: History/Timeline
1. View patient admission history
2. - [ ] Admission date shows IST
3. - [ ] Discharge date shows IST
4. - [ ] All timestamps in IST (if applicable)

### Task 4: Report Generation
1. If applicable, generate any reports
2. - [ ] Report timestamps in IST
3. - [ ] Consistent formatting across report

## Performance Testing

### Response Time
- [ ] Dashboard loads in < 2 seconds
- [ ] AJAX requests complete in < 500ms
- [ ] No additional server load
- [ ] Database queries unchanged

### Data Integrity
- [ ] No data corruption
- [ ] Existing records display correctly
- [ ] No timezone conversion errors
- [ ] Sorting by date works correctly

## Browser Timezone Independence Testing

**Goal:** Verify times display as IST regardless of browser timezone

### Test Procedure
1. Simulate different timezones:
   - Set browser to UTC
   - Set browser to IST
   - Set browser to EST
   - Set browser to Singapore (SGT)

2. Check dashboard times:
   - [ ] Always show same IST time regardless of browser timezone
   - [ ] Never show UTC or other timezone

### How to Test (Chrome DevTools)
1. Open DevTools (F12)
2. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)
3. Type "Emulate timezone" or use Settings → Overrides
4. Select different timezone
5. Refresh page
6. - [ ] Times still show correct IST (not affected by browser tz)

## Rollback Testing

**Optional:** Verify rollback works if needed

Rollback steps:
1. Revert `settings.py` TIME_ZONE to 'UTC'
2. - [ ] AJAX endpoint still works
3. - [ ] Times show in UTC again
4. Restore to IST:
5. - [ ] Times back to IST

## Documentation Verification

- [ ] User can understand how to use IST filters
- [ ] Code comments explain timezone conversion
- [ ] Examples provided for common scenarios
- [ ] Troubleshooting guide helpful

## Security Testing

- [ ] No timezone info leakage
- [ ] Times display doesn't expose sensitive data
- [ ] CSRF tokens still working in AJAX
- [ ] Authentication unaffected

## Deployment Checklist

### Before Going Live
- [ ] All tests passed
- [ ] Reviewed settings.py changes
- [ ] Confirmed custom_filters.py is correct
- [ ] Backend timezone conversion verified
- [ ] No breaking changes to existing API

### Production Environment
- [ ] Apply settings.py changes to production
- [ ] Push custom_filters.py to production
- [ ] Update views.py with timezone conversion
- [ ] Update templates with `{% load custom_filters %}`
- [ ] Clear Django cache (if applicable)
- [ ] Verify DST settings (if applicable in Asia/Kolkata)

### Post-Deployment
- [ ] Monitor for any timezone-related errors
- [ ] Check user reports about time display
- [ ] Verify all date fields show IST
- [ ] Test audit logs (if applicable)
- [ ] Document any issues found

## Common Issues & Verification

### Issue: Times still showing UTC
**Check:**
- [ ] Is `TIME_ZONE = 'Asia/Kolkata'` in settings.py?
- [ ] Did you restart Django after changing settings?
- [ ] Is `USE_TZ = True` set?
- [ ] Did you clear browser cache?

**Fix:**
```bash
# Clear Django cache
python manage.py clear_cache

# Restart Django development server
python manage.py runserver
```

### Issue: Filter not found
**Check:**
- [ ] Template has `{% load custom_filters %}`?
- [ ] custom_filters.py exists in templatetags/?
- [ ] Did you restart Django?

**Fix:**
- Verify import at top of template: `{% load custom_filters %}`
- Check file exists: `hospital/templatetags/custom_filters.py`
- Restart Django

### Issue: AJAX dates wrong
**Check:**
- [ ] Backend has timezone conversion code?
- [ ] Check Network tab for actual response
- [ ] Verify response is IST formatted

**Fix:**
- Apply timezone conversion in views.py (already done)
- Restart Django
- Clear browser cache

## Success Criteria

✅ **All of these should be true:**

1. [ ] Doctor dashboard times show in IST
2. [ ] Prescription dates show in IST
3. [ ] Check-in times show in IST
4. [ ] AJAX responses include IST-formatted dates
5. [ ] Times match actual IST (UTC+5:30)
6. [ ] Custom filters work in templates
7. [ ] No errors in browser console
8. [ ] No errors in Django server logs
9. [ ] Performance unchanged
10. [ ] Works on all browsers
11. [ ] Works on mobile
12. [ ] Timezone independent (browser timezone doesn't affect display)
13. [ ] Existing data displays correctly
14. [ ] New records get correct timestamps
15. [ ] All documentation updated

## Sign-Off

- [ ] All checklist items completed
- [ ] Ready for production deployment
- [ ] Team notified of timezone change
- [ ] Users aware of IST display

---

**Verification Date:** April 23, 2026
**Timezone:** Asia/Kolkata (IST, UTC+5:30)
**Status:** ✅ Ready for Verification
