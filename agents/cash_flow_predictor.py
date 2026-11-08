"""Cash Flow Predictor Agent for FINORA AI.

Reuses modules.forecast_engine to project future cash balances.
Accounts for pending receivables and payables from the Excel database.
Calculates liquidity milestones and runway metrics deterministically;
Gemini provides natural-language narrative commentary.
"""

from typing import Any, Dict
import pandas as pd

from modules.forecast_engine import generate_cash_forecast
from modules.excel_manager import get_receivables, get_payables
from utils.openrouter_client import get_openrouter_client
from utils.logger import get_logger

logger = get_logger("cash_flow_predictor")


def run_cash_flow_predictor(forecast_days: int = 30) -> Dict[str, Any]:
    """Execute cash flow prediction agent workflow.

    Args:
        forecast_days: Forecast horizon in days. Defaults to 30.

    Returns:
        dict: Deterministic liquidity projections, milestone metrics, and commentary.
    """
    logger.info("Generating cash flow projection for %d days...", forecast_days)

    # 1. Deterministic Forecast Computation (reusing modules.forecast_engine)
    current_cash, forecast_df = generate_cash_forecast(forecast_days=forecast_days)

    # 2. Extract Key Financial Milestones
    min_cash = float(forecast_df["Projected Cash"].min())
    max_cash = float(forecast_df["Projected Cash"].max())
    min_row = forecast_df.loc[forecast_df["Projected Cash"].idxmin()]
    min_date_str = pd.to_datetime(min_row["Date"]).strftime("%d %B %Y")

    final_cash = float(forecast_df.iloc[-1]["Projected Cash"])
    net_change = final_cash - current_cash

    # Pending Receivables and Payables Totals
    receivables_df = get_receivables()
    payables_df = get_payables()

    pending_rec_total = 0.0
    if not receivables_df.empty and "Status" in receivables_df.columns:
        pending_rec = receivables_df[
            receivables_df["Status"].astype(str).str.strip().str.lower() == "pending"
        ]
        pending_rec_total = float(pd.to_numeric(pending_rec["Amount"], errors="coerce").fillna(0).sum())

    pending_pay_total = 0.0
    if not payables_df.empty and "Status" in payables_df.columns:
        pending_pay = payables_df[
            payables_df["Status"].astype(str).str.strip().str.lower() == "pending"
        ]
        pending_pay_total = float(pd.to_numeric(pending_pay["Amount"], errors="coerce").fillna(0).sum())

    # Runway estimation: count of days before cash becomes negative (if any)
    negative_days = forecast_df[forecast_df["Projected Cash"] < 0]
    runway_days = len(forecast_df) if negative_days.empty else int((negative_days.iloc[0]["Date"] - forecast_df.iloc[0]["Date"]).days)

    prediction_results = {
        "current_cash": current_cash,
        "forecast_days": forecast_days,
        "forecast_df": forecast_df,
        "min_projected_cash": min_cash,
        "min_projected_date": min_date_str,
        "max_projected_cash": max_cash,
        "final_projected_cash": final_cash,
        "net_projected_change": net_change,
        "pending_receivables": pending_rec_total,
        "pending_payables": pending_pay_total,
        "runway_days": runway_days,
    }

    # 3. Natural-Language Commentary via OpenRouter AI
    ai_client = get_openrouter_client()
    commentary = ai_client.explain_cash_forecast(prediction_results)
    prediction_results["commentary"] = commentary

    logger.info("Cash flow forecast completed successfully.")
    return prediction_results


if __name__ == "__main__":
    results = run_cash_flow_predictor(30)
    print("\n--- FINORA AI CASH FLOW PREDICTOR AGENT ---")
    print(f"Current Available Cash: ₹{results['current_cash']:,.2f}")
    print(f"Lowest Projected Cash: ₹{results['min_projected_cash']:,.2f} on {results['min_projected_date']}")
    print(f"Projected Net Change: ₹{results['net_projected_change']:,.2f}")
    print(f"Pending Receivables: ₹{results['pending_receivables']:,.2f}")
    print(f"Pending Payables: ₹{results['pending_payables']:,.2f}")
    print("\n[Natural-Language Commentary]")
    print(results["commentary"])

