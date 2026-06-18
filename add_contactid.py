#Add account ID in contacts.csv
import pandas as pd

df_src = pd.read_csv('data/Contacts_exports.csv')
df_dest= pd.read_csv('data/leads_withconverted_acc.csv')


df_dest['Contact Id'] = df_dest['Phone'].map(
    df_src.set_index('Phone')['Record Id']
)

df_dest.to_csv("leads_withconverted_cont.csv", index=False)