# Create tasks.csv, meeting.csv, calls.csv using cofig_activites

import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import config
import config_activities as config

MIN_QUOTES_PER_ACCOUNT = 1
MAX_QUOTES_PER_ACCOUNT = 8

def process_data():
    print(f"Loading data from {config.INPUT_FILE}...")
    try:
        df = pd.read_csv(config.INPUT_FILE)
    except FileNotFoundError:
        print(f"Warning: {config.INPUT_FILE} not found.")

    quotes=[]
    
    # Counters for sequential IDs
    quotes_counter=1
    
    # Since "no random dates" was requested, we use a deterministic baseline date
    start_date = datetime.strptime(config.START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(config.END_DATE, "%Y-%m-%d")

    for idx, row in df.iterrows():
        acc_id = df.at[idx, 'Record Id']
        # task = df_leads.at[idx, 'Subject'] # When generating meetings and calls only
        num_quotes = random.randint(MIN_QUOTES_PER_ACCOUNT, MAX_QUOTES_PER_ACCOUNT)
        # Generate quotes
        # fields: Quote_Id, Subject, QuoteTotal, QuoteDate, Account_Id
        for i in range(num_quotes): 
            random_days = random.randint(
            0,
            (end_date - start_date).days
        )           
            quotes.append({
                "Quote Id": quotes_counter,
                "Subject": random.choice(config.QUOTE_SUBJECTS),
                "Quote Total": round(random.uniform(50000, 2000000),2),
                "Quote Date": start_date + timedelta(days=random_days),
                "Account Id": acc_id
            })
            quotes_counter += 1
            
    # Save to CSVs. We ensure empty dataframes are created with columns if no records generated
    df_quotes = pd.DataFrame(quotes, columns=["Quote Id","Subject","Quote Total","Quote Date","Account Id"])
    
    print(f"Generated {len(df_quotes)} tasks, saving to {config.OUTPUT_FILE}...")
    df_quotes.to_csv(config.OUTPUT_FILE, index=False)
    
    print("\nAll relational datasets generated successfully!")

if __name__ == "__main__":
    process_data()
