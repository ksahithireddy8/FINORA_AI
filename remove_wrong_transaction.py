from openpyxl import load_workbook
from modules.excel_manager import EXCEL_FILE

workbook = load_workbook(EXCEL_FILE)
sheet = workbook["Transactions"]

rows_to_remove = []

# Find only the incorrect test transaction
for row in range(2, sheet.max_row + 1):

    date = sheet.cell(row, 1).value
    description = sheet.cell(row, 2).value
    transaction_type = sheet.cell(row, 3).value
    category = sheet.cell(row, 4).value
    amount = sheet.cell(row, 5).value

    if (
        str(description).strip().lower() == "electricity bill"
        and str(transaction_type).strip().lower() == "income"
        and str(category).strip().lower() == "sales"
        and amount is not None
        and abs(float(amount) - 0.01) < 0.000001
    ):
        rows_to_remove.append(row)

# Remove only if exactly one matching record exists
if len(rows_to_remove) == 1:

    sheet.delete_rows(rows_to_remove[0], 1)
    workbook.save(EXCEL_FILE)

    print("Incorrect test transaction removed successfully!")

elif len(rows_to_remove) == 0:

    print("No matching incorrect transaction found.")

else:

    print("Multiple matching records found.")
    print("No changes made. Please inspect manually.")

workbook.close()