"""Data Analyst Agent for FINORA AI.

Analyses historical financial transactions from CSV and/or Excel.
Identifies income and expense patterns, monthly movements, and department-wise budget health.
All financial calculations are deterministic Python operations; Gemini provides contextual explanation.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

from modules.financial_analyzer import analyze_financial_data
from utils.openrouter_client import get_openrouter_client
from utils.logger import get_logger

logger = get_logger("data_analyst")

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_DIR / "data" / "cash_flow_transactions.csv"


def run_data_analyst(file_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Execute historical data analysis agent workflow.

    Args:
        file_path: Path to the transactions CSV file. Defaults to data/cash_flow_transactions.csv.

    Returns:
        dict: Deterministic analysis metrics and Gemini-assisted insights.
    """
    target_path = Path(file_path) if file_path else DEFAULT_CSV_PATH

    if not target_path.exists():
        logger.error("Transactions CSV not found at %s", target_path)
        raise FileNotFoundError(f"Historical transactions dataset not found at: {target_path}")

    logger.info("Analyzing historical transactions from: %s", target_path.name)

    # 1. Deterministic Financial Analysis (reusing modules.financial_analyzer)
    raw_results = analyze_financial_data(target_path)

    department_expenses = raw_results["department_expenses"]
    top_dept = department_expenses.index[0] if not department_expenses.empty else "N/A"
    top_dept_amt = float(department_expenses.iloc[0]) if not department_expenses.empty else 0.0

    analysis_metrics = {
        "total_transactions": int(raw_results["total_transactions"]),
        "total_income": float(raw_results["total_income"]),
        "total_expenses": float(raw_results["total_expenses"]),
        "net_cash_flow": float(raw_results["net_cash_flow"]),
        "monthly_analysis": raw_results["monthly_analysis"],
        "department_expenses": raw_results["department_expenses"],
        "top_spending_department": top_dept,
        "top_department_amount": top_dept_amt,
        "total_budget": float(raw_results["total_budget"]),
        "actual_expenses": float(raw_results["actual_expenses"]),
        "budget_difference": float(raw_results["budget_difference"]),
    }

    # 2. Natural-Language Explanation via OpenRouter AI (Strictly explanatory, zero math)
    ai_client = get_openrouter_client()
    insights = ai_client.explain_historical_data(analysis_metrics)
    analysis_metrics["insights"] = insights

    logger.info("Historical data analysis completed successfully.")
    return analysis_metrics


if __name__ == "__main__":
    results = run_data_analyst()
    print("\n--- FINORA AI DATA ANALYST AGENT ---")
    print(f"Transactions: {results['total_transactions']}")
    print(f"Total Inflow: {results['total_income']:,.2f} (dataset amount)")
    print(f"Total Outflow: {results['total_expenses']:,.2f} (dataset amount)")
    print(f"Net Cash Flow: {results['net_cash_flow']:,.2f} (dataset amount)")
    print(f"Top Department: {results['top_spending_department']} ({results['top_department_amount']:,.2f} dataset amount)")
    print(f"Budget Difference: {results['budget_difference']:,.2f} (dataset amount)")
    print("\n[Natural-Language Insights]")
    print(results["insights"])

