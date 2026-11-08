"""Modules package for FINORA AI."""

from modules.excel_manager import (
    EXCEL_FILE,
    create_database,
    add_transaction,
    get_transactions,
    get_business,
    get_receivables,
    get_payables,
    get_settings
)
from modules.financial_analyzer import analyze_financial_data
from modules.forecast_engine import generate_cash_forecast
from modules.risk_detector import detect_cash_risks

__all__ = [
    "EXCEL_FILE",
    "create_database",
    "add_transaction",
    "get_transactions",
    "get_business",
    "get_receivables",
    "get_payables",
    "get_settings",
    "analyze_financial_data",
    "generate_cash_forecast",
    "detect_cash_risks"
]
