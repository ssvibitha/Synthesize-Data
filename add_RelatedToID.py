#Add account ID in contacts.csv
import pandas as pd

df_src = pd.read_csv('data/Leads_exports.csv')
df_dest= pd.read_csv('data/new_leads.csv')


df_dest['Record Id'] = df_dest['company'].map(
    df_src.set_index('Company')['Record Id']
)
df_dest.to_csv("new_leads1.csv", index=False)
print(df_dest.columns)

# df=pd.read_csv("new_leads_cleaned.csv")
# unique_name = df["name"].value_counts().sum() #9000
# unique_email=df["email"].value_counts().sum()#9000
# unique_phone = df["mobile"].value_counts().sum()#9000
# print("unique_email: ",unique_email)
# print("unique_name: ",unique_name)
# print("unique_phone: ",unique_phone)