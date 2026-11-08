import pandas as pd
from modules.excel_manager import EXCEL_FILE
from datetime import date, timedelta

print("EXCEL FILE:", EXCEL_FILE)
print("TODAY:", date.today())

for sheet_name in ["Receivables", "Payables"]:

    print("\n" + "=" * 40)
    print(sheet_name.upper())
    print("=" * 40)

    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name=sheet_name
    )

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    print("\nSAVED RECORDS:")
    print(df.to_string(index=False))

    if not df.empty:
        print("\nDATE CHECK:")

        for _, row in df.iterrows():

            due_date = pd.to_datetime(
                row.get("Due Date"),
                errors="coerce"
            )

            status = str(
                row.get("Status", "")
            ).strip().lower()

            print("Name:", row.iloc[0])
            print("Amount:", row.get("Amount"))
            print("Due Date:", due_date)
            print("Status:", status)

            if pd.notna(due_date):
                print(
                    "Inside next 30 days:",
                    date.today() <= due_date.date()
                    <= date.today() + timedelta(days=30)
                )

            print("-" * 25)