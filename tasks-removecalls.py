# use taske_leads to create meeting_leads, calls_leads
import pandas as pd
df = pd.read_csv("data/tasks_leads.csv")
df = df[df['Subject'] != 'Call']
df.to_csv("data/tasks_leads.csv",index=False)