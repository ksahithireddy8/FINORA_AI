"""Risk Detector Agent for FINORA AI.

Reuses modules.risk_detector to evaluate reserve shortages and negative cash.
Classifies risks into NORMAL, WARNING, or CRITICAL levels.
Generates structured risk indicators and OpenRouter AI-assisted contextual risk assessments.
"""

from typing import Any, Dict, Optional
import pandas as pd

from modules.risk_detector import detect_cash_risks
from utils.openrouter_client import get_openrouter_client
from utils.logger import get_logger

logger = get_logger("risk_detector_agent")


def run_risk_detector(minimum_reserve: float = 5000.0) -> Dict[str, Any]:
    """Execute risk detection agent workflow.

    Args:
        minimum_reserve: Threshold below which cash balance triggers a reserve warning.

    Returns:
        dict: Risk classification, metrics, daily breaches, and narrative assessment.
    """
    logger.info("Executing risk detection with minimum reserve threshold: ₹%s", f"{minimum_reserve:,.2f}")

    # 1. Deterministic Risk Detection (reusing modules.risk_detector)
    current_cash, forecast_df, risks = detect_cash_risks(minimum_reserve=minimum_reserve)

    # 2. Risk Classification & Milestone Extraction
    has_critical = any(r.get("Risk Level") == "CRITICAL" for r in risks)
    has_warning = any(r.get("Risk Level") == "WARNING" for r in risks)

    if has_critical:
        overall_level = "CRITICAL"
    elif has_warning:
        overall_level = "WARNING"
    else:
        overall_level = "NORMAL"

    risk_days_count = len(risks)
    earliest_date = "None"
    earliest_level = "NORMAL"
    earliest_shortage = 0.0
    max_shortage = 0.0

    if risks:
        first_risk = risks[0]
        earliest_date = pd.to_datetime(first_risk["Date"]).strftime("%d %B %Y")
        earliest_level = first_risk.get("Risk Level", "WARNING")
        earliest_shortage = float(first_risk.get("Reserve Shortage", 0.0))
        max_shortage = float(max(r.get("Reserve Shortage", 0.0) for r in risks))

    risk_results = {
        "overall_risk_level": overall_level,
        "minimum_reserve": minimum_reserve,
        "current_cash": current_cash,
        "risk_days_count": risk_days_count,
        "earliest_risk_date": earliest_date,
        "earliest_risk_level": earliest_level,
        "earliest_risk_shortage": earliest_shortage,
        "max_shortage": max_shortage,
        "risks": risks,
        "forecast_df": forecast_df
    }

    # 3. Natural-Language Risk Assessment via OpenRouter AI
    ai_client = get_openrouter_client()
    assessment = ai_client.explain_risks(risk_results)
    risk_results["assessment"] = assessment

    logger.info("Risk detection complete. Overall status: %s", overall_level)
    return risk_results


if __name__ == "__main__":
    results = run_risk_detector(5000.0)
    print("\n--- FINORA AI RISK DETECTOR AGENT ---")
    print(f"Overall Risk Status: {results['overall_risk_level']}")
    print(f"Total Days At Risk: {results['risk_days_count']}")
    print(f"Earliest Risk Date: {results['earliest_risk_date']}")
    print(f"Earliest Shortage: ₹{results['earliest_risk_shortage']:,.2f}")
    print(f"Max Shortage: ₹{results['max_shortage']:,.2f}")
    print("\n[Natural-Language Risk Assessment]")
    print(results["assessment"])

