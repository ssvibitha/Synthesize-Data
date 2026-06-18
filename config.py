"""
Configuration file for CRM data generation and transformation.
"""

# File paths
INPUT_FILE = "leads_withconverted.csv"   # Replace with your Kaggle dataset filename
OUTPUT_FILE = ".csv"

# 1. Columns to keep exactly as they are (before renaming)
# Only these columns will be loaded from the original dataset initially
COLUMNS_TO_KEEP = [
    "LeadID",
    "Last Name",
    "Phone",
    "Email",
    "Converted",
    "Company"
]

# 2. Rename columns
# Format: {'old_name': 'new_name'}
COLUMN_RENAMES = {
    "Company": "Account Name",
    "Last Name": "Contact Name"
}

# 3. New Features Generation Rules
# We define parameters here that the processing script will use to create new features.

# Example A: Constant value
DEFAULT_CURRENCY = "USD"

# Example B: Categories for a new random feature
CUSTOMER_SEGMENTS = ["Startup", "SMB", "Enterprise"]
SEGMENT_PROBABILITIES = [0.5, 0.3, 0.2] # Must sum to 1.0

# Example C: Date ranges for random date generation
ENROLLMENT_START_DATE = "2020-01-01"
ENROLLMENT_END_DATE = "2023-12-31"

# 4. Columns to drop at the very end (e.g., intermediate columns you used to build new ones)
COLUMNS_TO_DROP = [
    "LeadID",
    "Converted"  # Assuming we don't want to keep the original conversion status in the final dataset
]
