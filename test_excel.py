from modules.excel_manager import (
    EXCEL_FILE,
    add_transaction,
    get_transactions
)

print("EXCEL FILE LOCATION:")
print(EXCEL_FILE)

print("\nFILE EXISTS:")
print(EXCEL_FILE.exists())

# Read existing records
transactions = get_transactions()

# Avoid inserting the same test record repeatedly
already_exists = (
    not transactions.empty
    and (
        transactions["Description"] == "Excel Connection Test"
    ).any()
)

if not already_exists:

    add_transaction(
        "2026-11-06",
        "Excel Connection Test",
        "Income",
        "Sales",
        5000
    )

    print("\nNew test transaction added!")

else:
    print("\nTest transaction already exists.")

# Read Excel again after saving
updated_transactions = get_transactions()

print("\nUPDATED TRANSACTIONS:")
print(updated_transactions)

print("\nTOTAL RECORDS:", len(updated_transactions))

print("\nEXCEL TEST COMPLETED!")