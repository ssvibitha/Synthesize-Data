import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

def generate_random_dates(start_date, end_date, n):
    """Helper function to generate random dates between start and end."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    
    random_days = np.random.randint(0, delta.days + 1, size=n)
    return [start + timedelta(days=int(days)) for days in random_days]

def process_data():
    print(f"Loading data from {config.INPUT_FILE}...")
    try:
        # 1. Load only the columns we want to keep
        df = pd.read_csv(config.INPUT_FILE, usecols=config.COLUMNS_TO_KEEP)
    except FileNotFoundError:
        print(f"Warning: {config.INPUT_FILE} not found. Please place your Kaggle dataset in the same folder.")
        print("-> Falling back to generating a dummy dataframe for demonstration...\n")
        dummy_data = {
            "id": [1, 2, 3],
            "first_name": ["John", "Jane", "Alice"],
            "last_name": ["Doe", "Smith", "Johnson"],
            "email": ["john@example.com", "jane@example.com", "alice@example.com"],
            "country": ["USA", "UK", "Canada"],
            "status": ["active", "inactive", "active"],
            "amount": [150.50, 0.00, 2500.00]
        }
        df = pd.DataFrame(dummy_data)
        # Ensure we only keep what the config asked for (simulating the usecols behavior)
        df = df[[c for c in config.COLUMNS_TO_KEEP if c in df.columns]]

    df = df[df["Converted"] == "Yes"]
    print("Renaming columns...")
    # 2. Rename columns
    df = df.rename(columns=config.COLUMN_RENAMES)
    
    print("Adding new features...")
    df["ContactID"] = "C"+df.index.map(lambda x: f"{x+1:04d}")  # Example of adding a new feature: a unique account ID
    # 3. Add new features based on configuration
    num_rows = len(df)
    
    # Feature A: Combine names into a single column
    # (Assuming first_name and last_name were kept and not renamed)
    # if 'first_name' in df.columns and 'last_name' in df.columns:
    #     df['full_name'] = df['first_name'] + ' ' + df['last_name']
    
    # Feature B: Constant field
    # df['currency'] = config.DEFAULT_CURRENCY

    # Feature C: Random categorical assignment (e.g., segment)
    # df['customer_segment'] = np.random.choice(
    #     config.CUSTOMER_SEGMENTS, 
    #     size=num_rows, 
    #     p=config.SEGMENT_PROBABILITIES
    # )

    # Feature D: Random dates within a range
    # df['enrollment_date'] = generate_random_dates(
    #     config.ENROLLMENT_START_DATE, 
    #     config.ENROLLMENT_END_DATE, 
    #     num_rows
    # )

    # Feature E: Conditional logic based on existing data
    # Example: If lifetime_value > 1000, they are VIP
    # if 'lifetime_value' in df.columns: # Note we check the new name because it was already renamed
    #     df['is_vip'] = df['lifetime_value'] > 1000

    print("Cleaning up...")
    # 4. Drop columns that are no longer needed
    columns_to_drop = [col for col in config.COLUMNS_TO_DROP if col in df.columns]
    df = df.drop(columns=columns_to_drop)

    # 5. Export tailored dataset
    print(f"Saving tailored dataset to {config.OUTPUT_FILE}...")
    df.to_csv(config.OUTPUT_FILE, index=False)
    
    print("\nData Transformation Complete! Here is a preview of your tailored data:")
    print(df.head())

if __name__ == "__main__":
    process_data()
