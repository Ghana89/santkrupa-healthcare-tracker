import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')

import django
django.setup()

from hospital.models import Clinic, MasterTest

DEFAULT_TESTS = [
    {"test_name": "Complete Blood Count (CBC)", "test_type": "blood", "category": "Pathology", "description": "Measures RBC, WBC, hemoglobin, platelets"},
    {"test_name": "Blood Sugar (Fasting)", "test_type": "blood", "category": "Pathology", "description": "Measures fasting glucose level"},
    {"test_name": "HbA1c", "test_type": "blood", "category": "Pathology", "description": "Average blood sugar over 3 months"},
    {"test_name": "Lipid Profile", "test_type": "blood", "category": "Pathology", "description": "Measures cholesterol levels"},
    {"test_name": "Liver Function Test (LFT)", "test_type": "blood", "category": "Pathology", "description": "Checks liver health"},
    {"test_name": "Kidney Function Test (KFT)", "test_type": "blood", "category": "Pathology", "description": "Checks kidney health"},
    {"test_name": "ECG", "test_type": "ecg", "category": "Cardiology", "description": "Measures heart electrical activity"},
    {"test_name": "2D Echo", "test_type": "ecg", "category": "Cardiology", "description": "Ultrasound of heart"},
    {"test_name": "TMT (Stress Test)", "test_type": "ecg", "category": "Cardiology", "description": "Checks heart under stress"},
    {"test_name": "X-Ray", "test_type": "xray", "category": "Radiology", "description": "Basic imaging test"},
    {"test_name": "Ultrasound Abdomen", "test_type": "ultrasound", "category": "Radiology", "description": "Abdominal scan"},
    {"test_name": "CT Scan", "test_type": "ct_scan", "category": "Radiology", "description": "Detailed imaging"},
    {"test_name": "MRI Scan", "test_type": "mri", "category": "Radiology", "description": "Advanced imaging"},
    {"test_name": "Urine Routine", "test_type": "urine", "category": "Pathology", "description": "Basic urine analysis"},
    {"test_name": "Dengue Test", "test_type": "blood", "category": "Pathology", "description": "Detect dengue virus"},
    {"test_name": "Malaria Test", "test_type": "blood", "category": "Pathology", "description": "Detect malaria infection"},
]

def run():
    clinics = Clinic.objects.all()

    for clinic in clinics:
        # Delete all existing tests for this clinic
        deleted_count, _ = MasterTest.objects.filter(clinic=clinic).delete()
        print(f"Deleted {deleted_count} old tests for clinic: {clinic.name}")

        # Add new default tests
        for test in DEFAULT_TESTS:
            MasterTest.objects.create(
                clinic=clinic,
                test_name=test["test_name"],
                test_type=test["test_type"],
                category=test["category"],
                description=test["description"],
                is_active=True
            )
        print(f"Added {len(DEFAULT_TESTS)} default tests for clinic: {clinic.name}")

    print("✅ All clinics updated with default tests successfully!")

if __name__ == "__main__":
    run()