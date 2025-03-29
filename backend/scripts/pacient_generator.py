from faker import Faker
import pandas as pd
import random

fake = Faker()

COMMON_ALLERGIES = [
    "Penicillin", "Amoxicillin", "Cephalosporins", "Sulfa drugs", 
    "Aspirin", "Ibuprofen", "Naproxen", "Chemotherapy drugs",
    "Anticonvulsants", "Insulin",
    "Peanuts", "Tree nuts", "Shellfish", "Eggs", 
    "Milk", "Soy", "Wheat", "Sesame",
    "Latex", "Bee stings", "Dust mites", "Pollen",
    "Pet dander", "Mold", "Nickel", "Radio contrast dye",
    "Local anesthetics"
]

MEDICAL_CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "COPD",
    "Coronary artery disease", "Heart failure", "Atrial fibrillation",
    "Chronic kidney disease", "Osteoarthritis", "Rheumatoid arthritis",
    "Acute bronchitis", "Pneumonia", "Urinary tract infection", 
    "Gastroenteritis", "Migraine", "Depression", "Anxiety disorder",
    "Hyperthyroidism", "Hypothyroidism", "Anemia", "Osteoporosis",
    "Epilepsy", "Psoriasis", "Eczema"
]

MEDICATIONS = [
    "Paracetamol 500mg", "Ibuprofen 400mg", "Naproxen 250mg",
    "Diclofenac 50mg", "Celecoxib 200mg",
    "Amoxicillin 500mg", "Azithromycin 250mg", "Ciprofloxacin 500mg",
    "Doxycycline 100mg",
    "Atorvastatin 20mg", "Metoprolol 50mg", "Losartan 50mg",
    "Amlodipine 5mg", "Furosemide 40mg",
    "Metformin 850mg", "Insulin glargine", "Levothyroxine 50mcg",
    "Omeprazole 20mg", "Cetirizine 10mg", "Sertraline 50mg",
    "Alprazolam 0.5mg", "Warfarin 5mg"
]

patients = []
num_pac = 100

for _ in range(num_pac):
    # Definir alergias (50% chance de não ter alergias?)
    if random.random() < 0.5:
        allergies = ["None"]
    else:
        num_allergies = random.randint(1, 2)
        allergies = random.sample([a for a in COMMON_ALLERGIES if a != "None"], num_allergies)
    
    patients.append({
        "Name": fake.name(),
        "NIF": fake.ssn(),
        "Age": random.randint(18, 90),
        "Date of Birth": fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d-%m-%Y"),
        "Address": fake.address().replace('\n', ', '),
        "Phone": fake.phone_number(),
        "Email": fake.email(),
        "Blood Type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
        "Medical Condition": random.choice(MEDICAL_CONDITIONS),
        "Medication": random.choice(MEDICATIONS),
        "Allergies": allergies,
        "Condition Severity": random.choice(["Mild", "Moderate", "Severe"])
    })

# Converter para DataFrame e guardar
df = pd.DataFrame(patients)
df.to_csv("fake_patients_en.csv", index=False)
print(f"{num_pac} pacientes falsos gerados com sucesso!")