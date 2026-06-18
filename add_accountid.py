#Add account ID in contacts.csv
import pandas as pd

df_leads = pd.read_csv('leads_withconverted_acc.csv')
df_contact = pd.read_csv('contacts.csv')


df_contact['Account Id'] = df_contact['Phone'].map(
    df_leads.set_index('Phone')['Account Id']
)

df_contact.to_csv("contacts_acc.csv", index=False)