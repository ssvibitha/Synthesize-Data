import pandas as pd
import random
import config_activities as config

df = pd.read_csv(config.INPUT_FILE)
account_order_counts = (
        df.groupby("Account Id")
        .size()
        .to_dict()
    )
rows=[]
count =1
for acc_id,order_count in account_order_counts.items(): #Extract key,value from dictionary
    if order_count>=6:
        num_cases= random.randint(0,3)
    elif order_count >=3:
        num_cases = random.randint(1,5)
    else:
        num_cases = random.randint(2,8)
    for i in range(num_cases):
        rows.append({
            "Case Id":count,
            "Title": random.choice(config.CASE_TITLE),
            "Status": random.choices(config.CASE_STATUS, weights=[70,20,10],k=1)[0], #k=1 for no.of selection from CASE_STATUS, the result is a list so use [0]
            "Case Origin":random.choices(config.CASE_ORIGIN, weights=[50,25,20,5],k=1)[0],
            "Account Id": acc_id
        })
        count+=1

df_case = pd.DataFrame(rows,columns=["Case Id","Title","Status","Case Origin","Account Id"])
print(f"Generated {len(df_case)} tasks, saving to {config.OUTPUT_FILE}...")
df_case.to_csv(config.OUTPUT_FILE, index=False)

print("\nAll relational datasets generated successfully!")
