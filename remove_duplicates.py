from openpyxl import load_workbook
from modules.excel_manager import EXCEL_FILE

# Open the Excel workbook
workbook = load_workbook(EXCEL_FILE)

# Select Transactions sheet
sheet = workbook["Transactions"]

seen = set()
rows_to_delete = []

# Check every transaction, excluding the header
for row_number in range(2, sheet.max_row + 1):

    row_values = tuple(
        sheet.cell(row=row_number, column=col).value
        for col in range(1, sheet.max_column + 1)
    )

    if row_values in seen:
        rows_to_delete.append(row_number)
    else:
        seen.add(row_values)

# Delete duplicate rows from bottom to top
for row_number in reversed(rows_to_delete):
    sheet.delete_rows(row_number, 1)

# Save the updated workbook
workbook.save(EXCEL_FILE)

print("Duplicate cleanup completed!")
print("Duplicate rows removed:", len(rows_to_delete))
print("Unique transactions remaining:", len(seen))