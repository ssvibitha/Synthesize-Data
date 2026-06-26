# Create sales_orders.csv donr, changing code to generate invoices.csv
import pandas as pd
import random
from datetime import datetime, timedelta
import config_activities as config

def process_data():
    print(f"Loading data from {config.INPUT_FILE}...")
    try:
        df = pd.read_csv(config.INPUT_FILE)
    except FileNotFoundError:
        print(f"Warning: {config.INPUT_FILE} not found.")
    df["Due Date"] = pd.to_datetime(df["Due Date"])
    account_order_counts = (
        df.groupby("Account Id")
        .size()
        .to_dict()
    )
    invoices=[]
    account_invoices_rates={}
    for acc_id, order_count in account_order_counts.items():

        if order_count >= 5:
            delay=random.randint(-10, 5)
        elif order_count >= 2:
            delay=random.randint(0,20)
        else:
            delay=random.randint(15,90)


        account_invoices_rates[acc_id] = delay
        # Counters for sequential IDs
    
    # Since "no random dates" was requested, we use a deterministic baseline date

    for idx, row in df.iterrows():

        acc_id = row["Account Id"]

        delay = account_invoices_rates[acc_id]
        # Decide whether this quote becomes an order
        df.at[idx,"Delay Days"] = delay
        df.at[idx, "Payment Date"] = df.at[idx,"Due Date"]+pd.Timedelta(days=delay)

    df.to_csv(config.OUTPUT_FILE, index=False)
    
    print("\nAll relational datasets generated successfully!")

if __name__ == "__main__":
    process_data()