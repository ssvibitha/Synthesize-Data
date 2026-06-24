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

    account_order_counts = (
        df.groupby("Account Id")
        .size()
        .to_dict()
    )
    invoices=[]
    account_invoices_rates={}
    for acc_id, order_count in account_order_counts.items():

        if order_count >= 5:
            rate = random.uniform(0.9, 1.0)
        elif order_count >= 2:
            rate = random.uniform(0.7, 0.9)
        else:
            rate = random.uniform(0.4, 0.7)

        account_invoices_rates[acc_id] = rate
        # Counters for sequential IDs
    invoice_counter=1
    
    # Since "no random dates" was requested, we use a deterministic baseline date

    for idx, row in df.iterrows():

        acc_id = row["Account Id"]

        conversion_rate = account_invoices_rates[acc_id]
        # Decide whether this quote becomes an order
        if random.random() < conversion_rate:

            sub = row["Subject"]
            start_date = datetime.strptime(
                row["Order Date"],
                "%Y-%m-%d"
            )

            end_date = datetime.strptime(
                config.END_DATE,
                "%Y-%m-%d"
            )

            total = row["Order Total"]

            random_days = random.randint(
                0,
                (end_date - start_date).days
            )

            invoices.append({
                "Invoice Id": invoice_counter,
                "Subject": sub,
                "Invoice Total": round(
                    total * random.uniform(0.98, 1.02),
                    2
                ),
                "Invoice Date": start_date + timedelta(days=random_days),
                "Account Id": acc_id
            })

            invoice_counter += 1
    # Save to CSVs. We ensure empty dataframes are created with columns if no records generated
    df_quotes = pd.DataFrame(invoices, columns=["Invoice Id","Subject","Invoice Total","Invoice Date","Account Id"])
    
    print(f"Generated {len(df_quotes)} tasks, saving to {config.OUTPUT_FILE}...")
    df_quotes.to_csv(config.OUTPUT_FILE, index=False)
    
    print("\nAll relational datasets generated successfully!")

if __name__ == "__main__":
    process_data()