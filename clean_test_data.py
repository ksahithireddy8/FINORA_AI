from openpyxl import load_workbook
from modules.excel_manager import EXCEL_FILE

# Open the Excel workbook
workbook = load_workbook(EXCEL_FILE)

# Select Transactions sheet
sheet = workbook["Transactions"]

# Delete all transaction rows, keeping the header
if sheet.max_row > 1:
    sheet.delete_rows(2, sheet.max_row - 1)

# Save workbook
workbook.save(EXCEL_FILE)

print("Test transactions cleared successfully!")
print("Excel database is ready for real testing.")