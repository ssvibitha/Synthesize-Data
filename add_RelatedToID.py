#Add account ID in contacts.csv
import pandas as pd

df_src = pd.read_csv('data/Leads_exports.csv')
df_dest= pd.read_csv('new_contacts.csv')


df_dest['Lead Id'] = df_dest['Account Name'].map(
    df_src.set_index('Company')['Record Id']
)
df_dest = df_dest.drop("Account Id",axis=1)
df_dest.to_csv("contacts_9000.csv", index=False)
print(df_dest.columns)
print(df_dest["Lead Id"].value_counts().sum())

# df=pd.read_csv("new_leads_cleaned.csv")
# unique_name = df["name"].value_counts().sum() #9000
# unique_email=df["email"].value_counts().sum()#9000
# unique_phone = df["mobile"].value_counts().sum()#9000
# print("unique_email: ",unique_email)
# print("unique_name: ",unique_name)
# print("unique_phone: ",unique_phone)