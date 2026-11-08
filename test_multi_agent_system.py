"""Comprehensive automated test suite for FINORA AI Multi-Agent System.

Validates:
1. Excel database and modules
2. All six specialist agents individually
3. Gemini client offline resilience and deterministic behavior
4. LangGraph Master Orchestrator end-to-end execution
5. Error boundary resilience
"""

import unittest
from pathlib import Path
import pandas as pd

from modules.excel_manager import (
    get_business,
    get_transactions,
    get_receivables,
    get_payables,
    get_settings
)
from modules.forecast_engine import generate_cash_forecast
from modules.risk_detector import detect_cash_risks
from agents.data_analyst import run_data_analyst
from agents.cash_flow_predictor import run_cash_flow_predictor
from agents.risk_detector_agent import run_risk_detector as run_risk_agent
from agents.strategy_advisor import run_strategy_advisor
from agents.financial_report_agent import run_financial_report
from agents.orchestrator import run_multi_agent_system
from utils.gemini_client import get_gemini_client
from utils.logger import get_logger


class TestFinoraMultiAgentSystem(unittest.TestCase):
    """Test suite covering data, agents, and multi-agent orchestration."""

    def test_01_excel_database_read(self):
        """Verify Excel database sheets are accessible and populated."""
        business = get_business()
        self.assertFalse(business.empty, "Business sheet should not be empty.")
        self.assertIn("Opening Cash", business.columns)

        transactions = get_transactions()
        self.assertIn("Amount", transactions.columns)

        receivables = get_receivables()
        self.assertIn("Status", receivables.columns)

        payables = get_payables()
        self.assertIn("Status", payables.columns)

        settings = get_settings()
        self.assertFalse(settings.empty, "Settings sheet should not be empty.")

    def test_02_forecast_engine(self):
        """Verify forecast engine produces deterministic cumulative projection."""
        current_cash, forecast = generate_cash_forecast(30)
        self.assertIsInstance(current_cash, float)
        self.assertEqual(len(forecast), 31)  # today + 30 days
        self.assertIn("Projected Cash", forecast.columns)
        self.assertIn("Net Cash Flow", forecast.columns)

    def test_03_risk_detector_module(self):
        """Verify risk detector flags reserve shortage correctly."""
        current_cash, forecast, risks = detect_cash_risks(minimum_reserve=5000)
        self.assertIsInstance(risks, list)
        if risks:
            first = risks[0]
            self.assertIn("Risk Level", first)
            self.assertIn(first["Risk Level"], ["CRITICAL", "WARNING"])
            self.assertGreater(first["Reserve Shortage"], 0)

    def test_04_data_analyst_agent(self):
        """Verify Agent 1: Data Analyst Agent computes deterministic aggregates and insights."""
        result = run_data_analyst()
        self.assertGreater(result["total_transactions"], 0)
        self.assertIn("insights", result)
        self.assertIsInstance(result["insights"], str)
        self.assertGreater(len(result["insights"]), 20)

    def test_05_cash_flow_predictor_agent(self):
        """Verify Agent 2: Cash Flow Predictor Agent generates structured metrics & commentary."""
        result = run_cash_flow_predictor(30)
        self.assertIn("current_cash", result)
        self.assertIn("min_projected_cash", result)
        self.assertIn("commentary", result)
        self.assertIsInstance(result["commentary"], str)
        self.assertGreaterEqual(result["pending_receivables"], 0)
        self.assertGreaterEqual(result["pending_payables"], 0)

    def test_06_risk_detector_agent(self):
        """Verify Agent 3: Risk Detector Agent assigns overall risk posture and assessment."""
        result = run_risk_agent(minimum_reserve=5000.0)
        self.assertIn(result["overall_risk_level"], ["NORMAL", "WARNING", "CRITICAL"])
        self.assertIn("assessment", result)
        self.assertIsInstance(result["assessment"], str)

    def test_07_strategy_advisor_agent(self):
        """Verify Agent 4: Strategy Advisor Agent produces prioritized recommendations."""
        strategies = run_strategy_advisor(minimum_reserve=5000.0)
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)
        for s in strategies:
            self.assertIn("Priority", s)
            self.assertIn("Area", s)
            self.assertIn("Issue", s)
            self.assertIn("Recommendation", s)

    def test_08_financial_report_agent(self):
        """Verify Agent 5: Financial Report Agent generates Markdown and text documents."""
        state = {
            "current_cash": 24000.0,
            "overall_risk_level": "WARNING",
            "min_projected_cash": 4000.0,
            "min_projected_date": "18 November 2026",
            "pending_receivables": 15000.0,
            "pending_payables": 35000.0,
            "net_cash_flow": -33.8,
            "total_transactions": 228,
            "strategies": [
                {
                    "Priority": "HIGH",
                    "Area": "Cash Management",
                    "Issue": "Reserve breach imminent.",
                    "Recommendation": "Expedite customer receivables."
                }
            ]
        }
        report = run_financial_report(state)
        self.assertIn("executive_summary", report)
        self.assertIn("markdown_report", report)
        self.assertIn("text_report", report)
        self.assertIn("# FINORA AI", report["markdown_report"])
        self.assertIn("FINORA AI - BUSINESS FINANCIAL REPORT", report["text_report"])
        # Verify specific corrections
        self.assertIn("Opening cash adjusted for recorded transactions", report["markdown_report"])
        self.assertIn("Opening cash adjusted for recorded transactions", report["text_report"])
        self.assertIn("-33.80 (dataset amount)", report["markdown_report"])
        self.assertIn("-33.80 (dataset amount)", report["text_report"])
        self.assertIn("₹24,000.00", report["markdown_report"])  # Excel in INR

    def test_09_gemini_client_resilience(self):
        """Verify Gemini Client operates smoothly in fallback mode without crashing."""
        client = get_gemini_client()
        explanation = client.explain_historical_data({
            "total_transactions": 50,
            "total_income": 10000.0,
            "total_expenses": 8000.0,
            "net_cash_flow": 2000.0,
            "top_spending_department": "Sales",
            "top_department_amount": 3000.0,
            "total_budget": 9000.0,
            "actual_expenses": 8000.0,
            "budget_difference": 1000.0
        })
        self.assertIn("10,000.00", explanation)
        self.assertIn("dataset amount", explanation)
        self.assertNotIn("₹10,000.00", explanation)

    def test_10_master_orchestrator_workflow(self):
        """Verify Agent 6: Master Orchestrator full LangGraph pipeline runs end-to-end."""
        final_state = run_multi_agent_system(forecast_days=30, minimum_reserve=5000.0)
        self.assertEqual(len(final_state.get("errors", [])), 0, f"Workflow had errors: {final_state.get('errors')}")
        self.assertIn("executive_summary", final_state)
        self.assertIn("markdown_report", final_state)
        self.assertIn("text_report", final_state)
        self.assertIn("strategies", final_state)
        self.assertGreaterEqual(len(final_state.get("agent_logs", [])), 5)

    def test_11_orchestrator_error_resilience(self):
        """Verify Master Orchestrator gracefully handles missing inputs without crashing."""
        final_state = run_multi_agent_system(
            forecast_days=30,
            minimum_reserve=5000.0,
            csv_path="non_existent_historical_file.csv"
        )
        # Should record the error in errors list
        self.assertGreater(len(final_state.get("errors", [])), 0)
        # Downstream pipeline should still complete
        self.assertIn("executive_summary", final_state)
        self.assertIn("markdown_report", final_state)
        self.assertIn("strategies", final_state)

    def test_12_logger_integration(self):
        """Verify logger utility formats messages and prevents duplicate handlers."""
        log1 = get_logger("test_unit")
        handler_count = len(log1.handlers)
        self.assertGreaterEqual(handler_count, 1)

        # Calling again should not duplicate handlers
        log2 = get_logger("test_unit")
        self.assertEqual(len(log2.handlers), handler_count)


if __name__ == "__main__":
    unittest.main()
