# Lead csv file
import pandas as pd
import numpy
from faker import Faker
import random

rows = []
fake = Faker()

num_records = 9000

sources = [
    "Website",
    "Referral",
    "LinkedIn",
    "Event",
    "Email Campaign",
    "Cold Call",
    "Partner"
]

industries = [
    "IT",
    "Education",
    "Healthcare",
    "Retail",
    "Finance",
    "Manufacturing"
]

for i in range(1, num_records + 1):

    lead_id = f"L{i:05d}"
    name = fake.name()
    email = fake.email()
    mobile = fake.msisdn()[:10]
    company = fake.company()
    website = fake.url()

    source = random.choice(sources)
    industry = random.choice(industries)

    followups = random.randint(0, 10)

    # Lead score generation
    score = random.randint(20, 95)

    # Conversion logic
    conversion_score = 0

    # Lead score impact
    if score >= 80:
        conversion_score += 40
    elif score >= 60:
        conversion_score += 25
    else:
        conversion_score += 5

    # Follow-up impact
    if followups >= 5:
        conversion_score += 20
    elif followups >= 2:
        conversion_score += 10

    # Source impact
    source_weights = {
        "Referral": 20,
        "Partner": 15,
        "Website": 10,
        "LinkedIn": 10,
        "Event": 5,
        "Email Campaign": 5,
        "Cold Call": 0
    }

    conversion_score += source_weights[source]

    # Industry impact
    industry_weights = {
        "IT": 10,
        "Finance": 10,
        "Healthcare": 8,
        "Education": 8,
        "Manufacturing": 5,
        "Retail": 5
    }

    conversion_score += industry_weights[industry]

    # Random business uncertainty
    conversion_score += random.randint(-15, 15)

    isConverted = (
        "Yes"
        if conversion_score >= 50
        else "No"
    )

    rows.append([
        lead_id,
        name,
        email,
        mobile,
        company,
        website,
        source,
        industry,
        followups,
        score,
        isConverted
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "lead_id",
        "name",
        "email",
        "mobile",
        "company",
        "website",
        "source",
        "industry",
        "followups",
        "score",
        "isConverted"
    ]
)

df.to_csv("leads.csv", index=False)

print(df["isConverted"].value_counts())
print("\nConversion Rate:")
print((df["isConverted"] == "Yes").mean() * 100)

df.to_csv("leads.csv", index=False)