import pandas as pd
from pathlib import Path
from openpyxl import load_workbook

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Excel database location
DATA_DIR = PROJECT_DIR / "data"
EXCEL_FILE = DATA_DIR / "finora_data.xlsx"


# Function 1: Create database if it doesn't exist
def create_database():

    if EXCEL_FILE.exists():
        print("Database already exists!")
        return EXCEL_FILE

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    business = pd.DataFrame([
        {
            "Business Name": "Sample Grocery Store",
            "Opening Cash": 20000
        }
    ])

    transactions = pd.DataFrame(columns=[
        "Date", "Description", "Type", "Category", "Amount"
    ])

    receivables = pd.DataFrame(columns=[
        "Customer", "Amount", "Due Date", "Status"
    ])

    payables = pd.DataFrame(columns=[
        "Supplier", "Amount", "Due Date", "Status"
    ])

    settings = pd.DataFrame([
        {"Setting": "Minimum Cash Reserve", "Value": 5000},
        {"Setting": "Forecast Days", "Value": 30}
    ])

    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        business.to_excel(writer, sheet_name="Business", index=False)
        transactions.to_excel(writer, sheet_name="Transactions", index=False)
        receivables.to_excel(writer, sheet_name="Receivables", index=False)
        payables.to_excel(writer, sheet_name="Payables", index=False)
        settings.to_excel(writer, sheet_name="Settings", index=False)

    return EXCEL_FILE


# Function 2: Add a transaction to Excel
def add_transaction(date, description, transaction_type,
                    category, amount):

    if not EXCEL_FILE.exists():
        raise FileNotFoundError("Excel database not found.")

    if transaction_type not in ["Income", "Expense"]:
        raise ValueError("Type must be Income or Expense.")

    if not description.strip():
        raise ValueError("Description cannot be empty.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook["Transactions"]

    sheet.append([
        str(date),
        description,
        transaction_type,
        category,
        float(amount)
    ])

    workbook.save(EXCEL_FILE)


# Function 3: Read all transactions
def get_transactions():

    return pd.read_excel(
        EXCEL_FILE,
        sheet_name="Transactions"
    )


# Function 4: Read business information
def get_business():

    return pd.read_excel(
        EXCEL_FILE,
        sheet_name="Business"
    )


# Function 5: Read customer receivables
def get_receivables():

    return pd.read_excel(
        EXCEL_FILE,
        sheet_name="Receivables"
    )


# Function 6: Read supplier payables
def get_payables():

    return pd.read_excel(
        EXCEL_FILE,
        sheet_name="Payables"
    )


# Function 7: Read business settings
def get_settings():

    return pd.read_excel(
        EXCEL_FILE,
        sheet_name="Settings"
    )