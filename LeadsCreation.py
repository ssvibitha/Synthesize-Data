import pandas as pd
from faker import Faker
import random
import os

fake = Faker()

num_records = 9000
file_path = "data/leads.csv"
contacts_path = "data/contacts.csv"
accounts_path = "data/accounts.csv"

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

existing_emails = set()
existing_mobiles = set()
existing_companies = set()
existing_names = set()

start_id = 1
start_contact_id = 1
start_account_id = 1

# Extract existing leads data
if os.path.exists(file_path):
    try:
        existing_df = pd.read_csv(file_path)
        if 'email' in existing_df.columns:
            existing_emails = set(existing_df['email'].dropna().astype(str))
        elif 'Email' in existing_df.columns:
            existing_emails = set(existing_df['Email'].dropna().astype(str))
            
        if 'mobile' in existing_df.columns:
            existing_mobiles = set(existing_df['mobile'].dropna().astype(str))
        elif 'Phone' in existing_df.columns:
            existing_mobiles = set(existing_df['Phone'].dropna().astype(str))
            
        if 'company' in existing_df.columns:
            existing_companies = set(existing_df['company'].dropna().astype(str))
        elif 'Company' in existing_df.columns:
            existing_companies = set(existing_df['Company'].dropna().astype(str))
            
        if 'name' in existing_df.columns:
            existing_names = set(existing_df['name'].dropna().astype(str))
        elif 'Last Name' in existing_df.columns:
            existing_names = set(existing_df['Last Name'].dropna().astype(str))
            
        if 'lead_id' in existing_df.columns:
            ids = existing_df['lead_id'].astype(str).str.extract(r'L(\d+)')[0].dropna().astype(int)
            if not ids.empty:
                start_id = ids.max() + 1
        elif 'Lead ID' in existing_df.columns:
            if existing_df['Lead ID'].dtype == 'O':
                ids = existing_df['Lead ID'].astype(str).str.extract(r'L?(\d+)')[0].dropna().astype(int)
            else:
                ids = existing_df['Lead ID'].dropna().astype(int)
            if not ids.empty:
                start_id = ids.max() + 1
    except Exception as e:
        print(f"Could not parse existing leads.csv: {e}")

# Extract existing contacts data to find max ContactID
if os.path.exists(contacts_path):
    try:
        cont_df = pd.read_csv(contacts_path)
        if 'ContactID' in cont_df.columns:
            ids = cont_df['ContactID'].dropna().astype(str).str.extract(r'(\d+)')[0].dropna().astype(int)
            if not ids.empty:
                start_contact_id = ids.max() + 1
    except Exception as e:
        pass

# Extract existing accounts data to find max AccountID
if os.path.exists(accounts_path):
    try:
        acc_df = pd.read_csv(accounts_path)
        if 'AccountID' in acc_df.columns:
            ids = acc_df['AccountID'].dropna().astype(str).str.extract(r'(\d+)')[0].dropna().astype(int)
            if not ids.empty:
                start_account_id = ids.max() + 1
    except Exception as e:
        pass

rows = []
contacts_rows = []
accounts_rows = []

generated_count = 0
current_id = start_id
current_contact_id = start_contact_id
current_account_id = start_account_id

while generated_count < num_records:
    firstname = fake.first_name()
    lastname = fake.last_name()
    name = f"{firstname} {lastname}"
    
    email = fake.email()
    mobile = fake.msisdn()[:10]
    company = fake.company()
    
    # Check uniqueness against existing leads.csv to prevent duplicates
    if email in existing_emails or mobile in existing_mobiles or company in existing_companies or name in existing_names:
        continue
        
    existing_emails.add(email)
    existing_mobiles.add(mobile)
    existing_companies.add(company)
    existing_names.add(name)

    lead_id = f"L{current_id:05d}"
    website = fake.url()

    source = random.choice(sources)
    industry = random.choice(industries)

    followups = random.randint(0, 10)

    # Lead score generation
    score = random.randint(20, 95)

    # Conversion logic
    conversion_score = 0

    if score >= 80:
        conversion_score += 40
    elif score >= 60:
        conversion_score += 25
    else:
        conversion_score += 5

    if followups >= 5:
        conversion_score += 20
    elif followups >= 2:
        conversion_score += 10

    source_weights = {
        "Referral": 20, "Partner": 15, "Website": 10, "LinkedIn": 10,
        "Event": 5, "Email Campaign": 5, "Cold Call": 0
    }
    conversion_score += source_weights[source]

    industry_weights = {
        "IT": 10, "Finance": 10, "Healthcare": 8,
        "Education": 8, "Manufacturing": 5, "Retail": 5
    }
    conversion_score += industry_weights[industry]

    conversion_score += random.randint(-15, 15)

    isConverted = "Yes" if conversion_score >= 50 else "No"

    rows.append([
        lead_id, name, email, mobile, company,
        website, source, industry, isConverted
    ])
    
    # If the lead is converted, add them to contacts and accounts
    if isConverted == "Yes":
        # Account
        accounts_rows.append([
            mobile, company, website, industry, current_account_id
        ])
        
        # Contact
        contacts_rows.append([
            name, email, mobile, company, current_contact_id, current_account_id
        ])
        
        current_account_id += 1
        current_contact_id += 1
    
    current_id += 1
    generated_count += 1

# Save Leads
new_df = pd.DataFrame(
    rows,
    columns=[
        "lead_id", "name", "email", "mobile", 
        "company", "website", "source", "industry", "isConverted"
    ]
)

new_file_path = "new_leads.csv"
new_contacts_path = "new_contacts.csv"
new_accounts_path = "new_accounts.csv"

new_df.to_csv(new_file_path, index=False)
print(f"Created {new_file_path} with {num_records} records")

# Save Contacts
if contacts_rows:
    new_contacts_df = pd.DataFrame(
        contacts_rows,
        columns=["Contact Name", "Email", "Phone", "Account Name", "ContactID", "Account Id"]
    )
    new_contacts_df.to_csv(new_contacts_path, index=False)
    print(f"Created {new_contacts_path} with {len(contacts_rows)} records")

# Save Accounts
if accounts_rows:
    new_accounts_df = pd.DataFrame(
        accounts_rows,
        columns=["Phone", "Account Name", "Website", "Industry", "AccountID"]
    )
    new_accounts_df.to_csv(new_accounts_path, index=False)
    print(f"Created {new_accounts_path} with {len(accounts_rows)} records")

print("\nValue Counts of isConverted for NEW records:")
print(new_df["isConverted"].value_counts())
print("\nConversion Rate for NEW records:")
print((new_df["isConverted"] == "Yes").mean() * 100)