"""OpenRouter AI Client for FINORA AI.

Integrates OpenRouter's OpenAI-compatible API (https://openrouter.ai/api/v1)
for natural-language financial explanations, insights, and executive summaries.

Key Architecture Principles:
- Strictly explanatory layer: OpenRouter AI provides narrative reasoning and summaries.
- ALL financial calculations, balances, and forecasts remain deterministic Python operations.
- Graceful offline fallback: if OPENROUTER_API_KEY is missing or the request fails,
  deterministic template narratives take over seamlessly.
- Security: API keys are read from .env and NEVER printed, logged, or exposed.
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from utils.logger import get_logger

load_dotenv()

logger = get_logger("openrouter_client")

# OpenRouter standard base URL and fallback model
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "google/gemini-2.5-flash"


class OpenRouterClient:
    """Resilient client for OpenRouter OpenAI-compatible API with deterministic fallback."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.active_model = model or os.getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
        self.client = None
        self.is_available = False

        if not self.api_key:
            logger.info("No OPENROUTER_API_KEY detected in environment. Operating in deterministic offline mode.")
            return

        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "https://finora.ai",
                    "X-Title": "FINORA AI"
                }
            )
            self.is_available = True
            logger.info("OpenRouter Client initialized successfully with model: %s", self.active_model)
        except Exception as e:
            logger.warning("Failed to initialize OpenRouter client: %s. Using fallback mode.", type(e).__name__)
            self.client = None
            self.is_available = False

    def test_connection(self) -> Dict[str, Any]:
        """Perform a safe API connection test without exposing or printing the API key.

        Returns:
            dict: Status summary with keys 'status', 'model', and 'message'.
        """
        if not self.api_key:
            return {
                "status": "offline",
                "model": self.active_model,
                "message": "No OPENROUTER_API_KEY configured in .env. Running in offline template mode."
            }

        if not self.is_available or self.client is None:
            return {
                "status": "error",
                "model": self.active_model,
                "message": "OpenRouter client is not initialized."
            }

        try:
            # Safe minimal ping request
            response = self.client.chat.completions.create(
                model=self.active_model,
                messages=[{"role": "user", "content": "Respond with 'OK' for connection check."}],
                max_tokens=5
            )
            if response and response.choices and response.choices[0].message:
                return {
                    "status": "connected",
                    "model": self.active_model,
                    "message": f"Successfully connected to OpenRouter API using model '{self.active_model}'."
                }
            return {
                "status": "error",
                "model": self.active_model,
                "message": "Empty response received from OpenRouter API."
            }
        except Exception as e:
            # Sanitize error message to ensure no keys or tokens leak
            error_type = type(e).__name__
            logger.warning("OpenRouter API connection test failed: %s", error_type)
            return {
                "status": "error",
                "model": self.active_model,
                "message": f"Connection test failed ({error_type}). Reverting to offline template mode."
            }

    def generate_content(self, prompt: str, fallback_text: str) -> str:
        """Generate text using OpenRouter API with automatic fallback.

        Args:
            prompt: Instructions and pre-calculated deterministic context for AI.
            fallback_text: Pre-computed deterministic explanation if OpenRouter is offline/fails.

        Returns:
            str: Generated explanation or fallback text.
        """
        if not self.is_available or self.client is None:
            return fallback_text

        try:
            response = self.client.chat.completions.create(
                model=self.active_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are FINORA AI's financial intelligence assistant. Maintain high accuracy."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            if response and response.choices and response.choices[0].message:
                text = response.choices[0].message.content
                if text:
                    return text.strip()
        except Exception as e:
            logger.warning("OpenRouter API call failed (%s). Reverting to deterministic template narrative.", type(e).__name__)

        return fallback_text

    def explain_historical_data(self, metrics: Dict[str, Any]) -> str:
        """Generate natural-language explanation of historical financial performance."""
        net = metrics.get("net_cash_flow", 0)
        net_status = "positive net cash flow (surplus)" if net >= 0 else "net cash deficit (burn)"
        top_dept = metrics.get("top_spending_department", "N/A")
        top_dept_amt = metrics.get("top_department_amount", 0)
        budget_diff = metrics.get("budget_difference", 0)
        budget_status = "under budget (favorable variance)" if budget_diff >= 0 else "over budget (unfavorable variance)"

        fallback = (
            f"Historical Analysis Summary:\n"
            f"- The business processed {metrics.get('total_transactions', 0)} transactions with "
            f"{metrics.get('total_income', 0):,.2f} total inflows (dataset amount) and {metrics.get('total_expenses', 0):,.2f} total outflows (dataset amount).\n"
            f"- This resulted in a {net_status} of {abs(net):,.2f} (dataset amount).\n"
            f"- Top operational expenditure was concentrated in '{top_dept}' at {top_dept_amt:,.2f} (dataset amount).\n"
            f"- Overall spending was {budget_status} by {abs(budget_diff):,.2f} (dataset amount) against the allocated budget."
        )

        if not self.is_available:
            return fallback

        prompt = (
            "You are FINORA AI's Senior Financial Analyst. Review these pre-calculated deterministic financial figures "
            "for a small business historical dataset (recorded as dataset amounts; do not display ₹ or assume currency for historical dataset figures) "
            "and write a clear, concise 3-4 sentence natural-language briefing highlighting key performance "
            "patterns and departmental budget health. Label amounts as dataset amounts:\n\n"
            f"Total Transactions: {metrics.get('total_transactions', 0)}\n"
            f"Total Cash Inflow: {metrics.get('total_income', 0):,.2f} (dataset amount)\n"
            f"Total Cash Outflow: {metrics.get('total_expenses', 0):,.2f} (dataset amount)\n"
            f"Net Cash Flow: {net:,.2f} (dataset amount)\n"
            f"Highest Spending Department: {top_dept} ({top_dept_amt:,.2f} dataset amount)\n"
            f"Total Budget: {metrics.get('total_budget', 0):,.2f} (dataset amount)\n"
            f"Actual Expenses: {metrics.get('actual_expenses', 0):,.2f} (dataset amount)\n"
            f"Budget Difference: {budget_diff:,.2f} (dataset amount)\n"
        )
        return self.generate_content(prompt, fallback)

    def explain_cash_forecast(self, forecast_summary: Dict[str, Any]) -> str:
        """Generate natural-language commentary for the 30-day cash forecast."""
        current_cash = forecast_summary.get("current_cash", 0)
        min_cash = forecast_summary.get("min_projected_cash", 0)
        min_date = forecast_summary.get("min_projected_date", "N/A")
        net_change = forecast_summary.get("net_projected_change", 0)
        receivables_total = forecast_summary.get("pending_receivables", 0)
        payables_total = forecast_summary.get("pending_payables", 0)

        trend = "an upward accumulation" if net_change >= 0 else "a net drawdown"

        fallback = (
            f"Cash Flow Forecast Commentary:\n"
            f"- Starting liquidity stands at ₹{current_cash:,.2f}.\n"
            f"- Over the 30-day projection period, the cash balance reflects {trend} of ₹{abs(net_change):,.2f}.\n"
            f"- The lowest projected liquidity point is expected on {min_date} at ₹{min_cash:,.2f}.\n"
            f"- Cash movements incorporate ₹{receivables_total:,.2f} in pending customer receivables and "
            f"₹{payables_total:,.2f} in upcoming supplier obligations."
        )

        if not self.is_available:
            return fallback

        prompt = (
            "You are FINORA AI's Cash Flow Predictor. Provide a concise 3-4 sentence professional commentary "
            "summarizing the upcoming 30-day liquidity trajectory for business management based on these deterministic numbers. "
            "Do NOT recalculate or modify numbers:\n\n"
            f"Current Cash Balance: ₹{current_cash:,.2f}\n"
            f"Lowest Projected Cash Balance: ₹{min_cash:,.2f} on {min_date}\n"
            f"30-Day Net Cash Movement: ₹{net_change:,.2f}\n"
            f"Pending Customer Inflows: ₹{receivables_total:,.2f}\n"
            f"Pending Supplier Outflows: ₹{payables_total:,.2f}\n"
        )
        return self.generate_content(prompt, fallback)

    def explain_risks(self, risk_summary: Dict[str, Any]) -> str:
        """Generate natural-language assessment of detected cash risks."""
        level = risk_summary.get("overall_risk_level", "NORMAL")
        first_date = risk_summary.get("earliest_risk_date", "None")
        max_shortage = risk_summary.get("max_shortage", 0)
        risk_days_count = risk_summary.get("risk_days_count", 0)

        if level == "CRITICAL":
            headline = "CRITICAL: Severe liquidity shortage detected where projected balances drop below zero."
        elif level == "WARNING":
            headline = "WARNING: Cash balance is projected to breach the required minimum cash reserve."
        else:
            headline = "NORMAL: Cash reserves remain adequately capitalized throughout the entire forecast horizon."

        fallback = (
            f"Risk Assessment Overview:\n"
            f"- Status: {headline}\n"
            f"- Number of days at risk: {risk_days_count} days.\n"
            f"- Earliest anticipated risk date: {first_date}.\n"
            f"- Maximum anticipated reserve shortage: ₹{max_shortage:,.2f}."
        )

        if not self.is_available:
            return fallback

        prompt = (
            "You are FINORA AI's Risk Detector Agent. Review this risk analysis and write a concise, impactful 2-3 sentence "
            "risk briefing emphasizing whether the business faces critical insolvency, reserve depletion, or stable liquidity:\n\n"
            f"Overall Risk Classification: {level}\n"
            f"Total Days At Risk: {risk_days_count}\n"
            f"Earliest Risk Date: {first_date}\n"
            f"Maximum Reserve Shortage: ₹{max_shortage:,.2f}\n"
            f"Minimum Reserve Threshold: ₹{risk_summary.get('minimum_reserve', 5000):,.2f}\n"
        )
        return self.generate_content(prompt, fallback)

    def generate_executive_summary(self, full_state: Dict[str, Any]) -> str:
        """Synthesize a complete multi-agent executive briefing."""
        current_cash = full_state.get("current_cash", 0)
        risk_level = full_state.get("overall_risk_level") or full_state.get("risk_level", "NORMAL")
        pending_rec = full_state.get("pending_receivables") or full_state.get("pending_receivables_total", 0)
        pending_pay = full_state.get("pending_payables") or full_state.get("pending_payables_total", 0)

        fallback = (
            f"Executive Financial Briefing:\n"
            f"FINORA AI has evaluated the latest business accounts. Available cash is ₹{current_cash:,.2f} "
            f"with an overall risk rating of {risk_level}. Pending customer receivables stand at ₹{pending_rec:,.2f} "
            f"against supplier payables of ₹{pending_pay:,.2f}. Timely collection of outstanding receivables is recommended "
            f"to safeguard cash reserves against upcoming obligations."
        )

        if not self.is_available:
            return fallback

        prompt = (
            "You are FINORA AI's Chief Financial Intelligence Agent. Write a high-level 4-5 sentence Executive Summary "
            "for the business owner synthesizing historical trends, cash projections, liquidity risks, and strategic guidance. "
            "Maintain an authoritative, supportive tone for a small business owner. Stick strictly to these deterministic inputs:\n\n"
            f"Current Cash: ₹{current_cash:,.2f}\n"
            f"Overall Risk Status: {risk_level}\n"
            f"Pending Receivables: ₹{pending_rec:,.2f}\n"
            f"Pending Payables: ₹{pending_pay:,.2f}\n"
            f"Historical Net Cash Movement: {full_state.get('net_cash_flow', 0):,.2f} (dataset amount)\n"
            f"Budget Difference: {full_state.get('budget_difference', 0):,.2f} (dataset amount)\n"
            f"Key Strategy Count: {len(full_state.get('strategies', []))}\n"
        )
        return self.generate_content(prompt, fallback)


# Global singleton instance
_openrouter_client_instance: Optional[OpenRouterClient] = None


def get_openrouter_client() -> OpenRouterClient:
    """Return the global OpenRouterClient instance."""
    global _openrouter_client_instance
    if _openrouter_client_instance is None:
        _openrouter_client_instance = OpenRouterClient()
    return _openrouter_client_instance


# Aliases for backwards compatibility
GeminiClient = OpenRouterClient
get_gemini_client = get_openrouter_client
get_ai_client = get_openrouter_client

