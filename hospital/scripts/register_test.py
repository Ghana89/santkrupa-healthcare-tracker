import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')

import django
django.setup()

# ✅ IMPORT AFTER SETUP
from hospital.models import Clinic, MasterTest


DEFAULT_TESTS = [
    {"test_name": "Complete Blood Count (CBC)", "test_type": "lab", "category": "Pathology", "description": "Measures RBC, WBC, hemoglobin, platelets"},
    {"test_name": "Blood Sugar (Fasting)", "test_type": "lab", "category": "Pathology", "description": "Measures fasting glucose level"},
    {"test_name": "HbA1c", "test_type": "lab", "category": "Pathology", "description": "Average blood sugar over 3 months"},
    {"test_name": "Lipid Profile", "test_type": "lab", "category": "Pathology", "description": "Measures cholesterol levels"},
    {"test_name": "Liver Function Test (LFT)", "test_type": "lab", "category": "Pathology", "description": "Checks liver health"},
    {"test_name": "Kidney Function Test (KFT)", "test_type": "lab", "category": "Pathology", "description": "Checks kidney health"},
    {"test_name": "ECG", "test_type": "diagnostic", "category": "Cardiology", "description": "Measures heart electrical activity"},
    {"test_name": "2D Echo", "test_type": "diagnostic", "category": "Cardiology", "description": "Ultrasound of heart"},
    {"test_name": "TMT (Stress Test)", "test_type": "diagnostic", "category": "Cardiology", "description": "Checks heart under stress"},
    {"test_name": "X-Ray", "test_type": "imaging", "category": "Radiology", "description": "Basic imaging test"},
    {"test_name": "Ultrasound Abdomen", "test_type": "imaging", "category": "Radiology", "description": "Abdominal scan"},
    {"test_name": "CT Scan", "test_type": "imaging", "category": "Radiology", "description": "Detailed imaging"},
    {"test_name": "MRI Scan", "test_type": "imaging", "category": "Radiology", "description": "Advanced imaging"},
    {"test_name": "Urine Routine", "test_type": "lab", "category": "Pathology", "description": "Basic urine analysis"},
    {"test_name": "Dengue Test", "test_type": "lab", "category": "Pathology", "description": "Detect dengue virus"},
    {"test_name": "Malaria Test", "test_type": "lab", "category": "Pathology", "description": "Detect malaria infection"},
]


def run():
    clinics = Clinic.objects.all()

    for clinic in clinics:
        for test in DEFAULT_TESTS:
            MasterTest.objects.get_or_create(
                clinic=clinic,
                test_name=test["test_name"],
                defaults={
                    "test_type": test["test_type"],
                    "category": test["category"],
                    "description": test["description"],
                    "is_active": True,
                }
            )

    print("✅ Default tests seeded successfully!")


# ✅ Optional: auto run when script executed
if __name__ == "__main__":
    run()