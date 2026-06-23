# Create campaign_members.csv to map each lead to a campaign along with member status

import pandas as pd
import random 
df = pd.read_csv("data/Leads_exports.csv")
rows=[]
campaigns = ["Website Lead Generation","Product Landing Page Launch","Summer Website Promotion",
                "Customer Referral Program","Partner Referral Drive","Referral Rewards Campaign",
                "LinkedIn Brand Awareness","LinkedIn Lead Generation","LinkedIn Sponsored Content",
                "Education Expo 2026","Tech Conference 2026","Industry Networking Event",
                "Outbound Prospecting Q1","SMB Outreach Campaign","Enterprise Calling Initiative"]
memberStatus = ["Planned","Invited","Sent","Received","Opened","Responded","Bounced","Opted Out"]
for idx,row in df.iterrows():
    lead_id = row['Record Id']
    rows.append({
                "Campaign Name": random.choice(campaigns),
                "Member Status": random.choice(memberStatus),
                "Lead ID": lead_id
            })

df = pd.DataFrame(rows, columns=["Campaign Name","Member Status","Lead ID"])
print(f"Generated {len(df)} rowa, saving to campaign_members.csv ...")
df.to_csv("campaign_members.csv", index=False)
