# Standard Prescription Template Implementation - Complete Guide

## Overview
This document provides a complete implementation of standard prescription templates functionality for doctors to save and reuse prescription templates.

## Features Implemented

### 1. **Database Models** (hospital/models.py - ALREADY ADDED)
Three new models have been added:
- `StandardPrescriptionTemplate`: Main template container
- `StandardTemplateMedicine`: Medicines in templates
- `StandardTemplateTest`: Tests in templates

### 2. **Forms** (hospital/forms.py - ALREADY ADDED)
- `StandardPrescriptionTemplateForm`: Create/edit templates
- `StandardTemplateMedicineForm`: Add medicines to templates
- `StandardTemplateTestForm`: Add tests to templates

### 3. **Views** (hospital/views.py - ALREADY ADDED)
Complete CRUD operations with AJAX support:
- `list_prescription_templates()`: List all templates
- `create_prescription_template()`: Create new template
- `view_prescription_template()`: View and manage template items
- `edit_prescription_template()`: Edit template details
- `delete_prescription_template()`: Delete entire template
- `delete_template_medicine()`: Remove medicine from template (AJAX)
- `delete_template_test()`: Remove test from template (AJAX)
- `search_prescription_templates()`: Search by keyword (AJAX)
- `load_template_to_prescription()`: Load template to prescription form (AJAX)
- `save_prescription_as_template()`: Save current prescription as template (AJAX)

### 4. **URLs** (santkrupa_hospital/urls.py - ALREADY ADDED)
```python
# All template URLs follow clinic-slug pattern
path('doctor/templates/', views.list_prescription_templates, name='list_prescription_templates'),
path('doctor/templates/create/', views.create_prescription_template, name='create_prescription_template'),
path('doctor/templates/<int:template_id>/', views.view_prescription_template, name='view_prescription_template'),
path('doctor/templates/<int:template_id>/edit/', views.edit_prescription_template, name='edit_prescription_template'),
path('doctor/templates/<int:template_id>/delete/', views.delete_prescription_template, name='delete_prescription_template'),
path('doctor/templates/search/', views.search_prescription_templates, name='search_prescription_templates'),
path('doctor/templates/<int:template_id>/load/', views.load_template_to_prescription, name='load_template_to_prescription'),
path('doctor/templates/medicine/<int:medicine_id>/delete/', views.delete_template_medicine, name='delete_template_medicine'),
path('doctor/templates/test/<int:test_id>/delete/', views.delete_template_test, name='delete_template_test'),
path('doctor/prescription/<int:prescription_id>/save-as-template/', views.save_prescription_as_template, name='save_prescription_as_template'),
```

### 5. **Templates** (HTML Files - ALREADY CREATED)
- `prescription_templates_list.html`: Display all templates with CRUD actions
- `prescription_template_form.html`: Create/edit template form
- `prescription_template_view.html`: View template, add/remove items
- `add_prescription_details.html`: UPDATED with template search and save buttons

### 6. **JavaScript** (AJAX Functionality - ALREADY CREATED)
- `prescription_templates.js`: Template search, load, and save functionality

### 7. **Dashboard** (UPDATED)
- `dashboard.html`: Added "Prescription Templates" card for quick access

## Database Migration

To create the tables in the database, run:

```bash
# Generate migrations
python manage.py makemigrations hospital

# Apply migrations
python manage.py migrate hospital
```

The generated migration will create:
- `hospital_standardprescriptiontemplate` table
- `hospital_standardtemplate medicine` table
- `hospital_standardtemplatetest` table

## Usage Workflow

### 1. **Create a Template**
- Doctor goes to Dashboard → Click "Prescription Templates"
- Click "Create New Template"
- Fill in template name, description, and search keyword
- Click "Save Template"
- Doctor is redirected to template view where they can add medicines and tests

### 2. **Add Medicines/Tests to Template**
-  On template view page, use the forms to add:
  - Medicines with dosage, frequency, duration, schedule, food instruction
  - Tests with type and description
- Click "Add Medicine" or "Add Test"
- Items appear in tables below

### 3. **Use Template When Creating Prescription**
- Doctor creates a new prescription for a patient
- In the "Add Prescription Details" page, look for "Quick Load Template" section
- Type a keyword (e.g., "fever", "cold") in the search box
- Suggestions appear based on template name, keyword, or description
- Click a template to automatically load all its medicines and tests
- Doctor can then edit fields as needed

### 4. **Save Current Prescription as Template**
- While creating/editing a prescription
- Click "Save as Template" button (top right)
- Fill in:
  - Template Name (required)
  - Description (optional)
  - Search Keyword (optional)
- Click "Save Template"
- The current prescription's medicines and tests are saved as a reusable template

### 5. **Manage Templates**
- Go to "Prescription Templates" page
- View all templates in a table
- Click edit icon (✏️) to modify template details
- Click delete icon (🗑️) to remove template
- Click view icon (👁️) to manage template items

## Key Features Explained

### Smart Search
- Search by template name
- Search by keyword (e.g., "fever", "pneumonia", "diabetes")
- Search by description
- Real-time suggestions as doctor types

### Field Editing
- After loading a template, all fields can be edited
- Doctor can modify dosage, frequency, duration per patient
- Add additional medicines/tests on top of template
- Remove unwanted medicines/tests

### Production-Grade Implementation

✅ **Security**
- Role-based access control (only doctors can access)
- Clinic-level isolation (doctors see only their clinic's templates)
- Doctor-specific templates (doctors see only their own)
- CSRF protection on all forms

✅ **Performance**
- Query optimization with `prefetch_related()` for medicines/tests
- Efficient AJAX calls for real-time operations
- Pagination support (limited to 10 search results)

✅ **User Experience**
- Responsive design with grid layouts
- Icons for quick visual identification
- Modal dialogs for save/load operations
- Confirmation dialogs for destructive actions
- Real-time success/error messages
- Loading feedback for AJAX operations

✅ **Data Integrity**
- Unique template names per doctor per clinic
- Cascading deletes (remove template removes all items)
- Proper foreign key relationships
- Field validation on all forms

## API Endpoints (AJAX)

### Search Templates
```
GET /clinic/{clinic_slug}/doctor/templates/search/?q=fever
Response: { templates: [{id, name, description, keyword, medicines_count, tests_count}] }
```

### Load Template
```
GET /clinic/{clinic_slug}/doctor/templates/{template_id}/load/
Response: { template_name, medicines: [...], tests: [...] }
```

### Save Prescription as Template
```
POST /clinic/{clinic_slug}/doctor/prescription/{prescription_id}/save-as-template/
Data: {template_name, template_description, template_keyword}
Response: {success, message, template_id}
```

### Delete Template Items (AJAX)
```
POST /clinic/{clinic_slug}/doctor/templates/medicine/{medicine_id}/delete/
POST /clinic/{clinic_slug}/doctor/templates/test/{test_id}/delete/
Response: {success}
```

## JavaScript Functions

The `prescription_templates.js` file provides:

1. **Template Search**
   - Real-time search suggestions
   - Debounced API calls (300ms)
   - Dropdown display of matching templates

2. **Template Loading**
   - `loadTemplate(templateId)`: Fetch template contents
   - Auto-populate form fields
   - Add medicines and tests to prescription

3. **Save as Template**
   - Modal dialog for template details
   - Form validation
   - Success/error handling

## Customization Options

### Modify Search Timeout
In `prescription_templates.js`, change:
```javascript
templateLoadTimeout = setTimeout(() => {
    // ...
}, 300);  // Change 300 to desired milliseconds
```

### Limit Search Results
In `search_prescription_templates()` view:
```python
templates[:10]  # Change 10 to desired limit
```

### Add More Template Fields
1. Add fields to `StandardPrescriptionTemplate` model
2. Update `StandardPrescriptionTemplateForm`
3. Update templates/views accordingly

## Troubleshooting

### Templates don't appear in search
- Check that templates are marked `is_active=True`
- Ensure doctor created the templates (not another doctor)
- Verify search query matches template name, keyword, or description

### Medicines/Tests not loading
- Check browser console for AJAX errors
- Verify clinic slug in URLs matches current clinic
- Check that medicines/tests exist in template

### Permissions error
- Verify user role is 'doctor'
- Ensure doctor is assigned to the clinic
- Check Django user permissions

## Files Created/Modified

### Created:
- `hospital/migrations/0051_standardprescriptiontemplate.py` (Migration file)
- `hospital/templates/hospital/doctor/prescription_templates_list.html`
- `hospital/templates/hospital/doctor/prescription_template_form.html`
- `hospital/templates/hospital/doctor/prescription_template_view.html`
- `hospital/templates/hospital/doctor/prescription_templates.js`

### Modified:
- `hospital/models.py` (Added 3 new models)
- `hospital/forms.py` (Added 3 new forms)
- `hospital/views.py` (Added 10 new views)
- `santkrupa_hospital/urls.py` (Added 10 new URL patterns)
- `hospital/templates/hospital/doctor/dashboard.html` (Added template card)
- `hospital/templates/hospital/doctor/add_prescription_details.html` (Added template search & save)

## Testing the Implementation

1. **Create a template:**
   - Login as doctor
   - Go to doctor dashboard
   - Click "Prescription Templates" card
   - Click "Create New Template"
   - Fill in details and save

2. **Add items to template:**
   - On template view, use forms to add medicines and tests
   - Verify items appear in tables

3. **Use template:**
   - Create new prescription for patient
   - Search for template in "Quick Load Template" section
   - Load template and verify all items appear
   - Edit fields and complete prescription

4. **Save as template:**
   - Create/edit prescription with medicines and tests
   - Click "Save as Template" button
   - Fill form and save
   - Verify in templates list

## Summary

This implementation provides:
- ✅ Complete CRUD for prescription templates
- ✅ Smart keyword-based search
- ✅ AJAX-powered real-time operations
- ✅ Template reuse to save doctor time
- ✅ Field editing for customization per patient
- ✅ Production-grade security and performance
- ✅ Professional UI/UX with modals and confirmations
- ✅ Full multi-tenant clinic support

The feature significantly improves workflow efficiency by allowing doctors to save time when creating prescriptions for common conditions.
