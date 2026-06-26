import pandas as pd
import random
df=pd.read_csv("data/account_health_historical.csv")
ch=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
w=[0.2,0.3,0.3,0.4,0.2,0.4,0.4,0.1,0.1,0.1]
df["Invoice Count"]=random.choices(ch,k=len(df))
print("Generating invoices...")
df.to_csv("Historical.csv",index=False)