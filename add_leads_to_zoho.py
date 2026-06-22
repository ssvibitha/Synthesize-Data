"""
Add 10 Leads to Zoho CRM via API

This script reads lead data from the CSV file and inserts 10 leads
into the Zoho CRM Leads module using the Zoho CRM REST API (v7).

Prerequisites:
  1. Register a "Self Client" at https://api-console.zoho.com/
  2. Generate a refresh token with scope: ZohoCRM.modules.leads.CREATE
  3. Create a .env file (see below) or set environment variables.

.env file format:
  ZOHO_CLIENT_ID=your_client_id
  ZOHO_CLIENT_SECRET=your_client_secret
  ZOHO_REFRESH_TOKEN=your_refresh_token
  ZOHO_API_DOMAIN=https://www.zohoapis.com      (use .in for India DC, .eu for EU, etc.)
  ZOHO_ACCOUNTS_URL=https://accounts.zoho.com    (use accounts.zoho.in for India DC, etc.)
"""

import csv
import json
import os
import sys
import time
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Try loading from .env file if python-dotenv is available.
# Use a safe fallback if the package is not installed to avoid import errors
try:
    # type: ignore
    from dotenv import load_dotenv
except Exception:
    # Provide a no-op fallback so callers can invoke load_dotenv() safely
    def load_dotenv():
        return None

# Call load_dotenv() to load environment variables if python-dotenv is present
load_dotenv()

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
API_DOMAIN = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")

# Path to your leads CSV (relative to this script)
CSV_FILE = os.path.join(os.path.dirname(__file__), "crm", "leads (1).csv")

# Number of leads to add
NUM_LEADS = 10


# ---------------------------------------------------------------------------
# Helper: Obtain Access Token via Refresh Token
# ---------------------------------------------------------------------------
def get_access_token() -> str:
    """Exchange the refresh token for a short-lived access token."""
    url = f"{ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    print("[AUTH] Requesting access token...")
    resp = requests.post(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "access_token" not in data:
        print(f"[AUTH ERROR] Response: {json.dumps(data, indent=2)}")
        sys.exit("Failed to obtain access token. Check your credentials.")

    print("[AUTH] Access token obtained successfully.")
    return data["access_token"]


# ---------------------------------------------------------------------------
# Helper: Read leads from CSV
# ---------------------------------------------------------------------------
def read_leads_from_csv(filepath: str, count: int) -> list[dict]:
    """
    Read `count` leads from the CSV and map them to Zoho CRM Lead fields.

    CSV columns:
      lead_id, name, email, mobile, company, website, source, industry,
      followups, score, isConverted

    Zoho CRM Leads module standard fields:
      Last_Name, Email, Mobile, Company, Website, Lead_Source, Industry
    """
    leads = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= count:
                break

            # Split full name into First_Name + Last_Name
            name_parts = row.get("name", "").strip().split(maxsplit=1)
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]

            lead = {
                "First_Name": first_name,
                "Last_Name": last_name,
                "Email": row.get("email", "").strip(),
                "Mobile": row.get("mobile", "").strip(),
                "Company": row.get("company", "").strip(),
                "Website": row.get("website", "").strip(),
                "Lead_Source": map_lead_source(row.get("source", "").strip()),
                "Industry": map_industry(row.get("industry", "").strip()),
                "Description": (
                    f"Imported from CSV | Lead ID: {row.get('lead_id', '')} | "
                    f"Score: {row.get('score', '')} | Followups: {row.get('followups', '')}"
                ),
            }
            leads.append(lead)

    return leads


def map_lead_source(source: str) -> str:
    """Map CSV source values to Zoho CRM's standard Lead_Source picklist."""
    mapping = {
        "Website": "Web Download",
        "Email Campaign": "Email",
        "Event": "Trade Show",
        "Partner": "Partner",
        "LinkedIn": "External Referral",
        "Referral": "External Referral",
        "Cold Call": "Cold Call",
    }
    return mapping.get(source, source if source else "None")


def map_industry(industry: str) -> str:
    """Map CSV industry values to Zoho CRM's standard Industry picklist."""
    mapping = {
        "Finance": "Finance",
        "IT": "Technology",
        "Healthcare": "Healthcare",
        "Retail": "Retail",
        "Education": "Education",
        "Manufacturing": "Manufacturing",
    }
    return mapping.get(industry, industry if industry else "None")


# ---------------------------------------------------------------------------
# Core: Insert Leads via Zoho CRM API
# ---------------------------------------------------------------------------
def insert_leads(access_token: str, leads: list[dict]) -> dict:
    """
    Insert leads into Zoho CRM using the bulk insert API.
    Zoho CRM allows up to 100 records per API call.
    """
    url = f"{API_DOMAIN}/crm/v7/Leads"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": leads,
        "trigger": ["workflow"],  # Trigger workflows on creation
    }

    print(f"\n[API] Inserting {len(leads)} leads into Zoho CRM...")
    print(f"[API] Endpoint: POST {url}")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Validate credentials ----
    missing = []
    if not CLIENT_ID:
        missing.append("ZOHO_CLIENT_ID")
    if not CLIENT_SECRET:
        missing.append("ZOHO_CLIENT_SECRET")
    if not REFRESH_TOKEN:
        missing.append("ZOHO_REFRESH_TOKEN")

    if missing:
        print("=" * 60)
        print("  ZOHO CRM API - ADD 10 LEADS")
        print("=" * 60)
        print()
        print("ERROR: Missing required credentials:")
        for m in missing:
            print(f"  - {m}")
        print()
        print("Setup instructions:")
        print("  1. Go to https://api-console.zoho.com/")
        print('  2. Create a "Self Client" application')
        print("  3. Generate a code with scope: ZohoCRM.modules.leads.CREATE")
        print("  4. Exchange the code for a refresh token")
        print()
        print("Then create a .env file in this directory:")
        print()
        print("  ZOHO_CLIENT_ID=1000.XXXXXXXXXX")
        print("  ZOHO_CLIENT_SECRET=abcdef1234567890")
        print("  ZOHO_REFRESH_TOKEN=1000.xxxxxxxxxxxx.yyyyyyyyyyyy")
        print("  ZOHO_API_DOMAIN=https://www.zohoapis.com")
        print("  ZOHO_ACCOUNTS_URL=https://accounts.zoho.com")
        print()
        print("For India datacenter, use:")
        print("  ZOHO_API_DOMAIN=https://www.zohoapis.in")
        print("  ZOHO_ACCOUNTS_URL=https://accounts.zoho.in")
        print()
        sys.exit(1)

    # ---- Read leads from CSV ----
    print("=" * 60)
    print("  ZOHO CRM API - ADD 10 LEADS")
    print("=" * 60)
    print()

    if not os.path.exists(CSV_FILE):
        sys.exit(f"CSV file not found: {CSV_FILE}")

    leads = read_leads_from_csv(CSV_FILE, NUM_LEADS)
    print(f"[CSV] Read {len(leads)} leads from: {CSV_FILE}")
    print()

    # ---- Preview leads ----
    print("-" * 60)
    print("  LEAD PREVIEW")
    print("-" * 60)
    for i, lead in enumerate(leads, 1):
        print(f"  {i:2d}. {lead['First_Name']} {lead['Last_Name']}")
        print(f"      Email:    {lead['Email']}")
        print(f"      Mobile:   {lead['Mobile']}")
        print(f"      Company:  {lead['Company']}")
        print(f"      Source:   {lead['Lead_Source']}")
        print(f"      Industry: {lead['Industry']}")
        print()

    # ---- Get access token ----
    access_token = get_access_token()

    # ---- Insert leads ----
    result = insert_leads(access_token, leads)

    # ---- Print results ----
    print()
    print("-" * 60)
    print("  RESULTS")
    print("-" * 60)

    success_count = 0
    error_count = 0

    for i, record in enumerate(result.get("data", []), 1):
        status = record.get("status", "unknown")
        code = record.get("code", "")
        message = record.get("message", "")
        details = record.get("details", {})
        record_id = details.get("id", "N/A")

        if status == "success":
            success_count += 1
            print(f"  {i:2d}. ✓ SUCCESS  | ID: {record_id} | {message}")
        else:
            error_count += 1
            print(f"  {i:2d}. ✗ FAILED   | Code: {code} | {message}")

    print()
    print("=" * 60)
    print(f"  SUMMARY: {success_count} succeeded, {error_count} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
