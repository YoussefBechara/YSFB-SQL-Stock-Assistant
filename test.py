import pandas as pd

# Load the Excel file
file_path = 'database.xlsx'  # Replace with the path to your Excel file
df = pd.read_excel(file_path)

# Drop the first 8856 rows
df = df.iloc[8856:]

# Save the modified DataFrame back to an Excel file
output_file_path = 'modified_file.xlsx'  # Replace with your desired output file path
df.to_excel(output_file_path, index=False)
