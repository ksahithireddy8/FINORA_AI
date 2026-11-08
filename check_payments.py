import pandas as pd
from modules.excel_manager import EXCEL_FILE

print("EXCEL DATABASE LOCATION:")
print(EXCEL_FILE)

print("\nDATABASE EXISTS:", EXCEL_FILE.exists())

# Read customer payments
receivables = pd.read_excel(
    EXCEL_FILE,
    sheet_name="Receivables"
)

# Read supplier payments
payables = pd.read_excel(
    EXCEL_FILE,
    sheet_name="Payables"
)

print("\n--- RECEIVABLES ---")

if receivables.empty:
    print("No customer payments found.")
else:
    print(receivables.to_string(index=False))

print("\n--- PAYABLES ---")

if payables.empty:
    print("No supplier payments found.")
else:
    print(payables.to_string(index=False))

print("\nTOTAL RECEIVABLE RECORDS:", len(receivables))
print("TOTAL PAYABLE RECORDS:", len(payables))