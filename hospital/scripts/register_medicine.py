import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')

import django
django.setup()

from hospital.models import Clinic, MasterMedicine


DEFAULT_MEDICINES = [

    # 🔴 Fever / Pain
    {
        "name": "Paracetamol",
        "type": "tablet",
        "dosage": "500mg, 650mg",
        "schedule": "morning_night",
        "duration": "3-5 days",
        "food": "after",
        "desc": "Used for fever and mild to moderate pain (headache, body pain)."
    },
    {
        "name": "Ibuprofen",
        "type": "tablet",
        "dosage": "400mg",
        "schedule": "morning_evening",
        "duration": "3 days",
        "food": "after",
        "desc": "Pain relief, inflammation, dental pain, muscle pain."
    },
    {
        "name": "Diclofenac",
        "type": "tablet",
        "dosage": "50mg",
        "schedule": "morning_night",
        "duration": "3 days",
        "food": "after",
        "desc": "Strong painkiller for joint pain, arthritis."
    },

    # 🔵 Antibiotics
    {
        "name": "Amoxicillin",
        "type": "capsule",
        "dosage": "500mg",
        "schedule": "morning_evening",
        "duration": "5 days",
        "food": "after",
        "desc": "Common antibiotic for throat, ear, and respiratory infections."
    },
    {
        "name": "Azithromycin",
        "type": "tablet",
        "dosage": "500mg",
        "schedule": "morning",
        "duration": "3 days",
        "food": "after",
        "desc": "Used for respiratory infections, typhoid, skin infections."
    },
    {
        "name": "Cefixime",
        "type": "tablet",
        "dosage": "200mg",
        "schedule": "morning_evening",
        "duration": "5 days",
        "food": "after",
        "desc": "Used in UTI, typhoid, respiratory infections."
    },

    # 🟡 Cold / Allergy
    {
        "name": "Cetirizine",
        "type": "tablet",
        "dosage": "10mg",
        "schedule": "night",
        "duration": "5 days",
        "food": "anytime",
        "desc": "Used for allergy, cold, sneezing, itching."
    },
    {
        "name": "Levocetirizine",
        "type": "tablet",
        "dosage": "5mg",
        "schedule": "night",
        "duration": "5 days",
        "food": "anytime",
        "desc": "Anti-allergic with less sedation."
    },

    # 🟠 Gastric
    {
        "name": "Pantoprazole",
        "type": "tablet",
        "dosage": "40mg",
        "schedule": "morning",
        "duration": "5 days",
        "food": "before",
        "desc": "Reduces acidity, GERD, gastric protection."
    },
    {
        "name": "Rabeprazole",
        "type": "tablet",
        "dosage": "20mg",
        "schedule": "morning",
        "duration": "5 days",
        "food": "before",
        "desc": "Used in acidity and stomach ulcers."
    },

    # 🔴 Diabetes
    {
        "name": "Metformin",
        "type": "tablet",
        "dosage": "500mg",
        "schedule": "morning_evening",
        "duration": "long-term",
        "food": "after",
        "desc": "First-line drug for type 2 diabetes."
    },

    # 🔵 BP / Heart
    {
        "name": "Amlodipine",
        "type": "tablet",
        "dosage": "5mg",
        "schedule": "morning",
        "duration": "long-term",
        "food": "after",
        "desc": "Used for high blood pressure."
    },
    {
        "name": "Losartan",
        "type": "tablet",
        "dosage": "50mg",
        "schedule": "morning",
        "duration": "long-term",
        "food": "after",
        "desc": "BP control and kidney protection in diabetes."
    },

    # 🟣 Vitamins
    {
        "name": "Vitamin D3",
        "type": "capsule",
        "dosage": "60000 IU",
        "schedule": "morning",
        "duration": "weekly",
        "food": "after",
        "desc": "Used for vitamin D deficiency and bone health."
    },
    {
        "name": "Calcium",
        "type": "tablet",
        "dosage": "500mg",
        "schedule": "morning_night",
        "duration": "30 days",
        "food": "after",
        "desc": "Bone strength and calcium deficiency."
    },

    # 🟤 Skin
    {
        "name": "Clotrimazole",
        "type": "ointment",
        "dosage": "apply",
        "schedule": "morning_night",
        "duration": "7 days",
        "food": "anytime",
        "desc": "Antifungal cream for skin infections."
    },

    # ⚫ Emergency / SOS
    {
        "name": "Ondansetron",
        "type": "tablet",
        "dosage": "4mg",
        "schedule": "sos",
        "duration": "as needed",
        "food": "anytime",
        "desc": "Used for vomiting and nausea."
    },
    {
        "name": "ORS",
        "type": "syrup",
        "dosage": "as needed",
        "schedule": "sos",
        "duration": "1 day",
        "food": "anytime",
        "desc": "Used in dehydration, diarrhea."
    },
]


def run():
    clinics = Clinic.objects.all()

    for clinic in clinics:
        for med in DEFAULT_MEDICINES:
            existing = MasterMedicine.objects.filter(
                clinic=clinic,
                medicine_name=med["name"]
            ).first()
            if not existing:
                MasterMedicine.objects.get_or_create(
                    clinic=clinic,
                    medicine_name=med["name"],
                    defaults={
                        "medicine_type": med["type"],
                        "common_dosages": med["dosage"],
                        "default_dosage": med["dosage"].split(",")[0],
                        "default_schedule": med["schedule"],
                        "default_duration": med["duration"],
                        "food_instruction": med["food"],
                        "description": med["desc"],  # ✅ NEW FIELD USED
                        "is_active": True,
                    }
                )

    print("✅ Medicines with descriptions added successfully!")


if __name__ == "__main__":
    run()