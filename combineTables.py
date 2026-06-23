# Select common columns to merge from table1 and table2 and create a new table
# (vertical stacking of 2 tables)

import pandas as pd

# 1. Define the columns you want to select from each CSV
# (Make sure the column names match exactly or rename them so they align)
selected_columns = ['Contact Name', 'Email', 'Phone', 'Account Name', 'ContactID',
       'Lead Id', 'Account Id']

# 2. Read only the selected columns from both CSV files
# Using 'usecols' is efficient because it only loads what you need into memory
df1 = pd.read_csv('data/contacts_9000.csv', usecols=selected_columns)
df2 = pd.read_csv('data/contacts.csv', usecols=selected_columns)

# 3. Combine (stack) the two dataframes vertically
# ignore_index=True ensures the internal index resets smoothly
combined_df = pd.concat([df1, df2], ignore_index=True)
print(len(combined_df))
# 4. Add a new incrementing ID column starting from 1
# We use insert() to place it as the very first column (position 0)
combined_df.insert(0, 'Contact Id', range(1, len(combined_df) + 1))

# 5. Save the combined data to a new CSV file
combined_df.to_csv('data/contacts_10000.csv', index=False)

print("Tables combined successfully! Preview:")
print(combined_df.head())