"""Financial Report Agent for FINORA AI.

Synthesizes outputs from all specialist agents:
- Historical Financial Performance (Data Analyst)
- 30-Day Liquidity Projections (Cash Flow Predictor)
- Reserve Shortages & Risk Status (Risk Detector)
- Strategic Mitigations (Strategy Advisor)

Produces comprehensive executive briefings and downloadable reports (Markdown & Plain Text).
"""

from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd

from utils.openrouter_client import get_openrouter_client
from utils.logger import get_logger

logger = get_logger("financial_report_agent")


def build_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generate a clean, structured Markdown financial report."""
    timestamp = report_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    exec_summary = report_data.get("executive_summary", "")
    current_cash = report_data.get("current_cash", 0.0)
    risk_level = report_data.get("overall_risk_level", "NORMAL")
    min_cash = report_data.get("min_projected_cash", 0.0)
    min_date = report_data.get("min_projected_date", "N/A")
    pending_rec = report_data.get("pending_receivables", 0.0)
    pending_pay = report_data.get("pending_payables", 0.0)

    # Historical
    hist_inflow = report_data.get("total_income", 0.0)
    hist_outflow = report_data.get("total_expenses", 0.0)
    hist_net = report_data.get("net_cash_flow", 0.0)
    hist_txns = report_data.get("total_transactions", 0)
    top_dept = report_data.get("top_spending_department", "N/A")
    top_dept_amt = report_data.get("top_department_amount", 0.0)

    # Risk info
    risk_days = report_data.get("risk_days_count", 0)
    max_shortage = report_data.get("max_shortage", 0.0)
    earliest_risk_date = report_data.get("earliest_risk_date", "None")

    strategies = report_data.get("strategies", [])

    lines = [
        "# FINORA AI — Business Financial Health Report",
        f"**Generated:** {timestamp}  ",
        f"**Risk Posture:** `{risk_level}`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        exec_summary,
        "",
        "---",
        "",
        "## 2. Key Financial Indicators",
        "| Indicator | Value | Status / Notes |",
        "| :--- | :--- | :--- |",
        f"| **Current Available Cash** | ₹{current_cash:,.2f} | Opening cash adjusted for recorded transactions |",
        f"| **Overall Risk Classification** | {risk_level} | {'⚠️ Action Required' if risk_level != 'NORMAL' else '✅ Well Capitalized'} |",
        f"| **Lowest Projected Cash** | ₹{min_cash:,.2f} | Expected on {min_date} |",
        f"| **Pending Receivables** | ₹{pending_rec:,.2f} | Outstanding customer invoices |",
        f"| **Pending Payables** | ₹{pending_pay:,.2f} | Upcoming vendor & operating bills |",
        f"| **Historical Net Cash Flow** | {hist_net:,.2f} (dataset amount) | {'Deficit (Burn)' if hist_net < 0 else 'Surplus'} (historical dataset) |",
        "",
        "---",
        "",
        "## 3. Historical Financial Analysis",
        f"- **Total Historical Transactions Analyzed:** {hist_txns}",
        f"- **Total Cash Inflow:** {hist_inflow:,.2f} (dataset amount)",
        f"- **Total Cash Outflow:** {hist_outflow:,.2f} (dataset amount)",
        f"- **Net Cash Movement:** {hist_net:,.2f} (dataset amount)",
        f"- **Primary Cost Driver:** {top_dept} ({top_dept_amt:,.2f} dataset amount)",
        f"- **Budget Health:** Budget variance is {report_data.get('budget_difference', 0.0):,.2f} (dataset amount)",
        "",
        "---",
        "",
        "## 4. 30-Day Liquidity & Risk Findings",
        f"- **Risk Days in Horizon:** {risk_days} day(s)",
        f"- **Earliest Identified Risk Date:** {earliest_risk_date}",
        f"- **Maximum Reserve Shortage:** ₹{max_shortage:,.2f}",
        f"- **Liquidity Assessment:** {report_data.get('risk_assessment', 'No significant liquidity threats detected.')}",
        "",
        "---",
        "",
        "## 5. Strategic Recommendations",
    ]

    if strategies:
        for idx, s in enumerate(strategies, start=1):
            lines.append(f"### Strategy {idx}: [{s.get('Priority', 'MEDIUM')}] {s.get('Area', 'General')}")
            lines.append(f"- **Identified Condition:** {s.get('Issue', '')}")
            lines.append(f"- **Recommended Action:** {s.get('Recommendation', '')}")
            lines.append("")
    else:
        lines.append("No immediate mitigation actions required. Maintain existing cash reserves.")

    lines.extend([
        "---",
        "*Report compiled by FINORA AI Multi-Agent Decision-Support System.*",
        "*Deterministic calculations verified via openpyxl & pandas.*"
    ])

    return "\n".join(lines)


def build_text_report(report_data: Dict[str, Any]) -> str:
    """Generate a plain-text financial report for raw terminal or text export."""
    timestamp = report_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines = [
        "============================================================",
        "          FINORA AI - BUSINESS FINANCIAL REPORT             ",
        "============================================================",
        f"Generated: {timestamp}",
        f"Overall Risk Status: {report_data.get('overall_risk_level', 'NORMAL')}",
        "------------------------------------------------------------",
        "EXECUTIVE SUMMARY:",
        report_data.get("executive_summary", ""),
        "------------------------------------------------------------",
        "KEY FINANCIAL METRICS:",
        f"  Current Available Cash   : ₹{report_data.get('current_cash', 0.0):,.2f} (Opening cash adjusted for recorded transactions)",
        f"  Lowest Projected Cash    : ₹{report_data.get('min_projected_cash', 0.0):,.2f} ({report_data.get('min_projected_date', 'N/A')})",
        f"  Pending Receivables      : ₹{report_data.get('pending_receivables', 0.0):,.2f}",
        f"  Pending Payables         : ₹{report_data.get('pending_payables', 0.0):,.2f}",
        f"  Historical Net Cash Flow : {report_data.get('net_cash_flow', 0.0):,.2f} (dataset amount)",
        "------------------------------------------------------------",
        "LIQUIDITY & RISK FINDINGS:",
        f"  Risk Days in Horizon     : {report_data.get('risk_days_count', 0)}",
        f"  Earliest Risk Date       : {report_data.get('earliest_risk_date', 'None')}",
        f"  Maximum Reserve Shortage : ₹{report_data.get('max_shortage', 0.0):,.2f}",
        "------------------------------------------------------------",
        "STRATEGIC RECOMMENDATIONS:"
    ]

    for idx, s in enumerate(report_data.get("strategies", []), start=1):
        lines.append(f"  {idx}. [{s.get('Priority')}] {s.get('Area')}")
        lines.append(f"     Issue : {s.get('Issue')}")
        lines.append(f"     Action: {s.get('Recommendation')}")

    lines.append("============================================================")
    return "\n".join(lines)


def run_financial_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute financial report agent workflow.

    Args:
        state: State dictionary containing outputs from prior agents.

    Returns:
        dict: Report package containing executive summary, markdown, and text report.
    """
    logger.info("Generating comprehensive business financial report...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct report payload
    report_payload = {**state, "timestamp": timestamp}

    # Generate Executive Summary via OpenRouter AI
    ai_client = get_openrouter_client()
    exec_summary = ai_client.generate_executive_summary(report_payload)
    report_payload["executive_summary"] = exec_summary

    # Build Markdown and Text Reports
    markdown_doc = build_markdown_report(report_payload)
    text_doc = build_text_report(report_payload)

    result = {
        "timestamp": timestamp,
        "executive_summary": exec_summary,
        "markdown_report": markdown_doc,
        "text_report": text_doc
    }

    logger.info("Financial report compiled successfully.")
    return result


if __name__ == "__main__":
    sample_state = {
        "current_cash": 24000.0,
        "overall_risk_level": "WARNING",
        "min_projected_cash": 4000.0,
        "min_projected_date": "18 November 2026",
        "pending_receivables": 15000.0,
        "pending_payables": 35000.0,
        "total_income": 244.0,
        "total_expenses": 277.8,
        "net_cash_flow": -33.8,
        "total_transactions": 228,
        "top_spending_department": "HR",
        "top_department_amount": 103.90,
        "budget_difference": -2.03,
        "risk_days_count": 20,
        "earliest_risk_date": "18 November 2026",
        "max_shortage": 1000.0,
        "strategies": [
            {
                "Priority": "HIGH",
                "Area": "Customer Receivables",
                "Issue": "Pending customer payments total ₹15,000.00.",
                "Recommendation": "Follow up with customers and request payment before the agreed due dates."
            }
        ]
    }
    report_out = run_financial_report(sample_state)
    print("\n--- FINORA AI FINANCIAL REPORT AGENT ---")
    print(report_out["markdown_report"][:600])
    print("\n... [truncated] ...")

