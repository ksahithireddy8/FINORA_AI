import pandas as pd
from datetime import date, timedelta

from modules.excel_manager import EXCEL_FILE


def generate_cash_forecast(forecast_days=30):

    # Read Excel sheets
    business = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Business"
    )

    transactions = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Transactions"
    )

    receivables = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Receivables"
    )

    payables = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Payables"
    )

    # Calculate current available cash
    opening_cash = float(
        business.iloc[0]["Opening Cash"]
    )

    income = transactions.loc[
        transactions["Type"] == "Income",
        "Amount"
    ].sum()

    expenses = transactions.loc[
        transactions["Type"] == "Expense",
        "Amount"
    ].sum()

    current_cash = opening_cash + income - expenses

    today = date.today()
    end_date = today + timedelta(days=forecast_days)

    # Prepare daily cash flow
    forecast = pd.DataFrame({
        "Date": pd.date_range(
            today,
            end_date,
            freq="D"
        )
    })

    forecast["Inflows"] = 0.0
    forecast["Outflows"] = 0.0

    # Add expected customer payments
    if not receivables.empty:

        for _, row in receivables.iterrows():

            status = str(row["Status"]).strip().lower()

            if status not in ["paid", "received", "completed"]:

                due_date = pd.to_datetime(
                    row["Due Date"],
                    errors="coerce"
                )

                if pd.notna(due_date):

                    due_date = due_date.normalize()

                    if due_date.date() < today:
                        due_date = pd.Timestamp(today)

                    if due_date <= pd.Timestamp(end_date):

                        forecast.loc[
                            forecast["Date"] == due_date,
                            "Inflows"
                        ] += float(row["Amount"])

    # Add expected supplier payments
    if not payables.empty:

        for _, row in payables.iterrows():

            status = str(row["Status"]).strip().lower()

            if status not in ["paid", "completed"]:

                due_date = pd.to_datetime(
                    row["Due Date"],
                    errors="coerce"
                )

                if pd.notna(due_date):

                    due_date = due_date.normalize()

                    if due_date.date() < today:
                        due_date = pd.Timestamp(today)

                    if due_date <= pd.Timestamp(end_date):

                        forecast.loc[
                            forecast["Date"] == due_date,
                            "Outflows"
                        ] += float(row["Amount"])

    # Calculate daily projected balance
    forecast["Net Cash Flow"] = (
        forecast["Inflows"] - forecast["Outflows"]
    )

    forecast["Projected Cash"] = (
        current_cash +
        forecast["Net Cash Flow"].cumsum()
    )

    # Return forecast results
    return current_cash, forecast


if __name__ == "__main__":

    current_cash, forecast = generate_cash_forecast(30)

    print("\nFINORA AI CASH FLOW FORECAST")

    print("Current Available Cash:", current_cash)

    print("\nNext 30 Days:")

    print(forecast.to_string(index=False))

    print("\nLowest Projected Cash:",
          forecast["Projected Cash"].min())
    print("\nForecast generated successfully!")