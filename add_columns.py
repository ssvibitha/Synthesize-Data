import pandas as pd
import random

df = pd.read_csv("data/cases.csv")

escalated=["API Integration Failure","Payment Not Reflected","Account Access Request","Refund Request"]
can_be_escalated=["New Integration Requirement","Configuration Assistance","Quote Revision Request"]

esc_list=[]
resolved_list=[]
for idx,row in df.iterrows():
    case_title= row["Title"]
    if case_title in escalated:
        esc=1
    elif case_title in can_be_escalated:
        esc = random.randint(0,1)
    else:
        esc=0
    esc_list.append(esc)
    
    stat = row["Status"]
    if stat =="Resolved" and esc == 1:
        d= random.randint(5,20)
    elif stat == "Resolved":
        d = random.randint(3,10)
    else:
        d = 0
    resolved_list.append(d)

df["Case Escalation"]=esc_list
df["ResolvedInDays"]=resolved_list

df.to_csv("data/cases_new.csv",index=False)
        



df.to_csv("data/cases_new.csv")