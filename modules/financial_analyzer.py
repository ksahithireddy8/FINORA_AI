import pandas as pd
from pathlib import Path


def analyze_financial_data(file_path):

    # Read historical CSV data
    df = pd.read_csv(file_path)

    # Calculate total cash inflow
    total_income = df["Cash Inflow"].sum()

    # Calculate total cash outflow
    total_expenses = df["Cash Outflow"].sum()

    # Calculate net cash flow
    net_cash_flow = total_income - total_expenses

    # Monthly analysis
    monthly_analysis = (
        df.groupby("Month")[
            ["Cash Inflow", "Cash Outflow"]
        ]
        .sum()
    )

    # Department-wise expenses
    department_expenses = (
        df.groupby("Department")["Cash Outflow"]
        .sum()
        .sort_values(ascending=False)
    )

    # Budget analysis
    total_budget = df["Budget Amount"].sum()
    actual_expenses = df["Actual Amount"].sum()

    budget_difference = total_budget - actual_expenses

    return {
        "total_transactions": len(df),
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cash_flow": net_cash_flow,
        "monthly_analysis": monthly_analysis,
        "department_expenses": department_expenses,
        "total_budget": total_budget,
        "actual_expenses": actual_expenses,
        "budget_difference": budget_difference
    }


if __name__ == "__main__":

    project_dir = Path(__file__).resolve().parents[1]

    file_path = (
        project_dir
        / "data"
        / "cash_flow_transactions.csv"
    )

    result = analyze_financial_data(file_path)

    print("\nFINORA AI FINANCIAL ANALYSIS")

    print("Total Transactions:",
          result["total_transactions"])

    print("Total Income:",
          result["total_income"])

    print("Total Expenses:",
          result["total_expenses"])

    print("Net Cash Flow:",
          result["net_cash_flow"])

    print("\nDepartment Expenses:")
    print(result["department_expenses"])

    print("\nBudget Difference:")
    print(result["budget_difference"])

    print("\nAnalysis completed successfully!")