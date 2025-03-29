from faker import Faker
import pandas as pd
import random

fake = Faker()

SPECIALTYS = [
    "Cardiology","Dermatology","Endocrinology",
    "Gastroenterology","Hematology","Immunology","Infectious Disease","Nephrology",
    "Neurology","Obstetrics and Gynecology","Oncology",
    "Ophthalmology","Orthopedics","Otolaryngology (ENT)",
    "Pediatrics","Psychiatry","Pulmonology","Radiology","Rheumatology",
    "Geriatrics","Sports Medicine","Allergy and Immunology","Nuclear Medicine","Family Medicine"
]

doctors = []
num_docs = 100

for i in range(num_docs):
    
    doctors.append({
        "Id": i,
        "Name": fake.name(),
        "Age": random.randint(18, 70),
        "Date of Birth": fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d-%m-%Y"),
        "Specialty": random.choice(SPECIALTYS),
        "Address": fake.address().replace('\n', ', '),
        "Phone": fake.phone_number(),
        "Email": fake.email(),
    })

# Converter para DataFrame e guardar
df = pd.DataFrame(doctors)
df.to_csv("fake_doctors_en.csv", index=False)
print(f"{num_docs} doutores falsos gerados com sucesso!")