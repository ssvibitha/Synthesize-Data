# Replace value for Lead_id from L001 to 1 

import pandas as pd
df = pd.read_csv("new_leads.csv")
df["lead_id"] = df["lead_id"].str.replace("L", "", regex=False).astype(int)
df = df.drop("isConverted",axis=1)
df.to_csv("new_leads_cleaned.csv", index=False)