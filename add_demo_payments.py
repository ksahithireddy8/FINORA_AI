from openpyxl import load_workbook
from modules.excel_manager import EXCEL_FILE
from datetime import date, timedelta

workbook = load_workbook(EXCEL_FILE)

today = date.today()

receivables = workbook["Receivables"]
payables = workbook["Payables"]


def add_if_missing(sheet, record):

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):
        if tuple(row[:4]) == tuple(record):
            print("Already exists:", record[0])
            return

    sheet.append(record)
    print("Added:", record[0])


# Customer payment: 4 days from today
add_if_missing(
    receivables,
    ["Demo Customer", 15000, today + timedelta(days=4), "Pending"]
)

# Supplier and business payments
demo_payments = [
    ["Demo Supplier", 25000, today + timedelta(days=6), "Pending"],
    ["Shop Rent", 8000, today + timedelta(days=9), "Pending"],
    ["Electricity Bill", 2000, today + timedelta(days=12), "Pending"]
]

for payment in demo_payments:
    add_if_missing(payables, payment)

workbook.save(EXCEL_FILE)
workbook.close()

print("\nDemo payment records saved!")