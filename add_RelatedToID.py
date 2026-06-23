# Add column from src to dest based on a common field
import pandas as pd

df_src = pd.read_csv('data/Accounts_exports.csv')
df_dest= pd.read_csv('data/contacts_9000.csv')

df_dest['Account Id'] = df_dest['Account Name'].map(
    df_src.set_index('Account Name')['Record Id']
)
df_dest.to_csv("contacts_9.csv", index=False)
print(df_dest.columns)

# Use when some records are Nan in mapping column
# In df_src, some rows have NaN in column 'Account Id'
# mapping = (
#     df_src
#     .dropna(subset=['Account Id'])
#     .set_index('Account Id')['Record Id']
# )

# df_dest['Lead ID'] = df_dest['Account Id'].map(mapping)

# df_dest.to_csv("contacts_leadId.csv", index=False)