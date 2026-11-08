"""Risk Detector Module for FINORA AI.

Evaluates cash flow projections against minimum reserve thresholds to identify
and classify financial risks (CRITICAL, WARNING, SAFE/NORMAL).
"""

from modules.forecast_engine import generate_cash_forecast


def detect_cash_risks(minimum_reserve=5000):
    """Detect potential cash flow risks over the next 30 days.

    Args:
        minimum_reserve: Minimum cash reserve amount threshold in currency units.

    Returns:
        tuple: (current_cash, forecast_df, risks_list)
    """
    # Generate the 30-day cash forecast
    current_cash, forecast = generate_cash_forecast(30)

    risks = []

    # Check each day's projected cash against the minimum reserve threshold
    for _, row in forecast.iterrows():
        projected_cash = float(row["Projected Cash"])

        if projected_cash < minimum_reserve:
            shortage = minimum_reserve - projected_cash

            risk = {
                "Date": row["Date"],
                "Projected Cash": projected_cash,
                "Risk Level": (
                    "CRITICAL"
                    if projected_cash < 0
                    else "WARNING"
                ),
                "Reserve Shortage": shortage
            }

            risks.append(risk)

    return current_cash, forecast, risks


if __name__ == "__main__":
    current_cash, forecast, risks = detect_cash_risks()

    print(f"Current Cash: {current_cash:,.2f}")
    print("\nCash Risks Detected:")

    if risks:
        for r in risks[:5]:
            print(r)
        if len(risks) > 5:
            print(f"... and {len(risks) - 5} more risk days.")
    else:
        print("No cash risks detected.")
