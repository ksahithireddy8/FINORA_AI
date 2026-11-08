from openpyxl import load_workbook
from modules.excel_manager import EXCEL_FILE
from datetime import date, timedelta

workbook = load_workbook(EXCEL_FILE)

today = date.today()

# Update customer payment date
receivables = workbook["Receivables"]

for row in range(2, receivables.max_row + 1):

    customer = receivables.cell(row, 1).value

    if customer == "Demo Customer":
        receivables.cell(row, 3).value = today + timedelta(days=4)
        print("Customer payment date updated")


# Update supplier payment dates
payables = workbook["Payables"]

demo_dates = {
    "Demo Supplier": 6,
    "Shop Rent": 9,
    "Electricity Bill": 12
}

for row in range(2, payables.max_row + 1):

    supplier = payables.cell(row, 1).value

    if supplier in demo_dates:
        days = demo_dates[supplier]

        payables.cell(row, 3).value = today + timedelta(days=days)

        print(supplier, "date updated")


workbook.save(EXCEL_FILE)
workbook.close()

print("\nAll demonstration dates updated!")
print("Forecast starting date:", today)