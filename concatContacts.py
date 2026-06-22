import pandas as pd

# Load the two CSV files
df1 = pd.read_csv('data/contacts.csv')
df2 = pd.read_csv('data/contacts_9000.csv')

# Concatenate them vertically (stacking them)
combined_df = pd.concat([df1, df2], ignore_index=True)

# Save the combined result to a new CSV file
combined_df.to_csv('combined_contacts.csv', index=False)

print(f"Successfully combined! Total records: {len(combined_df)}")