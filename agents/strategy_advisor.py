"""Strategy Advisor Agent for FINORA AI.

Generates evidence-based financial recommendations and risk mitigations.
Considers current liquidity, cash forecasts, detected risks, customer receivables,
and supplier payables to formulate prioritized action items.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from modules.risk_detector import detect_cash_risks
from modules.excel_manager import (
    get_receivables,
    get_payables
)
from utils.logger import get_logger

logger = get_logger("strategy_advisor")


def generate_strategies(
    current_cash: float,
    forecast: pd.DataFrame,
    risks: List[Dict[str, Any]],
    receivables: Optional[pd.DataFrame] = None,
    payables: Optional[pd.DataFrame] = None,
    minimum_reserve: float = 5000.0
) -> List[Dict[str, str]]:
    """Formulate deterministic, prioritized strategies based on financial metrics.

    Args:
        current_cash: Currently available cash.
        forecast: 30-day projection DataFrame.
        risks: List of detected risk events.
        receivables: DataFrame of customer receivables.
        payables: DataFrame of supplier payables.
        minimum_reserve: Minimum cash reserve amount threshold.

    Returns:
        list[dict]: Prioritized financial action cards.
    """
    strategies = []

    # 1. Current cash position
    if current_cash < minimum_reserve:
        strategies.append({
            "Priority": "HIGH",
            "Area": "Cash Management",
            "Issue": "Current cash is below the minimum reserve.",
            "Recommendation": (
                "Review immediate expenses and arrange sufficient "
                "funds to restore the cash reserve."
            )
        })
    else:
        strategies.append({
            "Priority": "NORMAL",
            "Area": "Cash Management",
            "Issue": "Current cash is above the minimum reserve.",
            "Recommendation": (
                "Monitor daily cash balances and maintain an "
                "emergency cash reserve."
            )
        })

    # 2. Future cash risk
    if risks:
        first_risk = risks[0]
        risk_date = pd.to_datetime(first_risk["Date"]).strftime("%d %B %Y")
        projected_cash = float(first_risk["Projected Cash"])
        shortage = float(first_risk["Reserve Shortage"])

        strategies.append({
            "Priority": "HIGH",
            "Area": "Future Cash Risk",
            "Issue": (
                f"Cash may fall below the reserve on {risk_date}. "
                f"Projected cash: ₹{projected_cash:,.2f}."
            ),
            "Recommendation": (
                f"Plan to improve available cash by at least "
                f"₹{shortage:,.2f} before {risk_date}."
            )
        })

    # 3. Customer receivables
    if receivables is not None and not receivables.empty:
        pending = receivables[
            receivables["Status"].astype(str).str.strip().str.lower() == "pending"
        ]

        if not pending.empty:
            pending_amount = pd.to_numeric(
                pending["Amount"],
                errors="coerce"
            ).fillna(0).sum()

            strategies.append({
                "Priority": "HIGH",
                "Area": "Customer Receivables",
                "Issue": (
                    f"Pending customer payments total "
                    f"₹{pending_amount:,.2f}."
                ),
                "Recommendation": (
                    "Follow up with customers and request payment "
                    "before the agreed due dates."
                )
            })

    # 4. Supplier payables
    if payables is not None and not payables.empty:
        pending_bills = payables[
            payables["Status"].astype(str).str.strip().str.lower() == "pending"
        ]

        if not pending_bills.empty:
            pending_amount = pd.to_numeric(
                pending_bills["Amount"],
                errors="coerce"
            ).fillna(0).sum()

            strategies.append({
                "Priority": "MEDIUM",
                "Area": "Supplier Payments",
                "Issue": (
                    f"Pending supplier payments total "
                    f"₹{pending_amount:,.2f}."
                ),
                "Recommendation": (
                    "Review upcoming supplier payment dates and "
                    "discuss revised schedules where necessary."
                )
            })

    # 5. Expense management
    strategies.append({
        "Priority": "MEDIUM",
        "Area": "Expense Management",
        "Issue": "Business expenses can affect future cash availability.",
        "Recommendation": (
            "Review non-essential expenses and postpone "
            "discretionary purchases when appropriate."
        )
    })

    return strategies


def run_strategy_advisor(
    current_cash: Optional[float] = None,
    forecast: Optional[pd.DataFrame] = None,
    risks: Optional[List[Dict[str, Any]]] = None,
    receivables: Optional[pd.DataFrame] = None,
    payables: Optional[pd.DataFrame] = None,
    minimum_reserve: float = 5000.0
) -> List[Dict[str, str]]:
    """Execute strategy advisor agent workflow.

    Reuses existing metrics when provided, or fetches them fresh.

    Args:
        current_cash: Optional starting cash balance.
        forecast: Optional forecast DataFrame.
        risks: Optional detected risks list.
        receivables: Optional receivables DataFrame.
        payables: Optional payables DataFrame.
        minimum_reserve: Minimum reserve threshold.

    Returns:
        list[dict]: Generated financial recommendations.
    """
    logger.info("Generating strategic financial recommendations...")

    # Fetch fresh data if not supplied
    if current_cash is None or forecast is None or risks is None:
        current_cash, forecast, risks = detect_cash_risks(minimum_reserve=minimum_reserve)

    if receivables is None:
        receivables = get_receivables()

    if payables is None:
        payables = get_payables()

    strategies = generate_strategies(
        current_cash=current_cash,
        forecast=forecast,
        risks=risks,
        receivables=receivables,
        payables=payables,
        minimum_reserve=minimum_reserve
    )

    logger.info("Generated %d strategic recommendations.", len(strategies))
    return strategies


if __name__ == "__main__":
    strategies = run_strategy_advisor()

    print("\nFINORA AI - STRATEGY ADVISOR")
    print("=" * 50)

    for index, strategy in enumerate(strategies, start=1):
        print(f"\nStrategy {index}")
        print("Priority:", strategy["Priority"])
        print("Area:", strategy["Area"])
        print("Issue:", strategy["Issue"])
        print("Recommendation:", strategy["Recommendation"])
