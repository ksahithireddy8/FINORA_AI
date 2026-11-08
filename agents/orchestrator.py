"""Master Orchestrator Agent for FINORA AI.

Orchestrates the multi-agent financial decision-support workflow using LangGraph.
Coordinates specialist agents:
  1. Data Analyst Agent (Historical transactions and departmental spending)
  2. Cash Flow Predictor Agent (30-day liquidity forecasting)
  3. Risk Detector Agent (Reserve shortages & negative cash classification)
  4. Strategy Advisor Agent (Evidence-based action recommendations)
  5. Financial Report Agent (Executive summary & downloadable reports)

Includes robust error containment, logging, and graceful fallbacks.
"""

from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime
import pandas as pd

from langgraph.graph import StateGraph, START, END

from agents.data_analyst import run_data_analyst
from agents.cash_flow_predictor import run_cash_flow_predictor
from agents.risk_detector_agent import run_risk_detector
from agents.strategy_advisor import run_strategy_advisor
from agents.financial_report_agent import run_financial_report
from utils.logger import get_logger

logger = get_logger("orchestrator")


class FinoraState(TypedDict, total=False):
    """Shared state object passed between specialist agents in the LangGraph workflow."""
    # Configuration & Metadata
    forecast_days: int
    minimum_reserve: float
    csv_path: Optional[str]
    agent_logs: List[str]
    errors: List[str]

    # 1. Data Analyst Outputs
    total_transactions: int
    total_income: float
    total_expenses: float
    net_cash_flow: float
    monthly_analysis: Any
    department_expenses: Any
    top_spending_department: str
    top_department_amount: float
    total_budget: float
    actual_expenses: float
    budget_difference: float
    data_insights: str

    # 2. Cash Flow Predictor Outputs
    current_cash: float
    forecast_df: Any
    min_projected_cash: float
    min_projected_date: str
    max_projected_cash: float
    final_projected_cash: float
    net_projected_change: float
    pending_receivables: float
    pending_payables: float
    runway_days: int
    forecast_commentary: str

    # 3. Risk Detector Outputs
    overall_risk_level: str
    risk_days_count: int
    earliest_risk_date: str
    earliest_risk_level: str
    earliest_risk_shortage: float
    max_shortage: float
    risks: List[Dict[str, Any]]
    risk_assessment: str

    # 4. Strategy Advisor Outputs
    strategies: List[Dict[str, str]]

    # 5. Financial Report Outputs
    executive_summary: str
    markdown_report: str
    text_report: str
    report_timestamp: str


# =====================================================================
# AGENT NODES FOR LANGGRAPH
# =====================================================================

def data_analyst_node(state: FinoraState) -> Dict[str, Any]:
    """Node 1: Execute historical data analysis."""
    logs = list(state.get("agent_logs", []))
    errors = list(state.get("errors", []))
    logger.info("Executing Node 1: Data Analyst Agent")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data Analyst Agent: Started historical data analysis.")

    try:
        csv_path = state.get("csv_path")
        results = run_data_analyst(file_path=csv_path)

        logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Data Analyst Agent: Processed "
            f"{results['total_transactions']} transactions. Net Movement: {results['net_cash_flow']:,.2f} (dataset amount)."
        )

        return {
            "total_transactions": results["total_transactions"],
            "total_income": results["total_income"],
            "total_expenses": results["total_expenses"],
            "net_cash_flow": results["net_cash_flow"],
            "monthly_analysis": results["monthly_analysis"],
            "department_expenses": results["department_expenses"],
            "top_spending_department": results["top_spending_department"],
            "top_department_amount": results["top_department_amount"],
            "total_budget": results["total_budget"],
            "actual_expenses": results["actual_expenses"],
            "budget_difference": results["budget_difference"],
            "data_insights": results["insights"],
            "agent_logs": logs,
            "errors": errors
        }
    except Exception as e:
        logger.error("Data Analyst Agent encountered an error: %s", e)
        errors.append(f"Data Analyst error: {str(e)}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data Analyst Agent: Error - {str(e)}")
        return {
            "total_transactions": 0,
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_cash_flow": 0.0,
            "top_spending_department": "N/A",
            "top_department_amount": 0.0,
            "total_budget": 0.0,
            "actual_expenses": 0.0,
            "budget_difference": 0.0,
            "data_insights": "Historical data unavailable due to error.",
            "agent_logs": logs,
            "errors": errors
        }


def cash_flow_predictor_node(state: FinoraState) -> Dict[str, Any]:
    """Node 2: Execute cash flow projection."""
    logs = list(state.get("agent_logs", []))
    errors = list(state.get("errors", []))
    logger.info("Executing Node 2: Cash Flow Predictor Agent")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Cash Flow Predictor Agent: Projecting liquidity.")

    try:
        days = state.get("forecast_days", 30)
        results = run_cash_flow_predictor(forecast_days=days)

        logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Cash Flow Predictor Agent: Forecast generated. "
            f"Current Cash: ₹{results['current_cash']:,.2f}, Lowest: ₹{results['min_projected_cash']:,.2f} on {results['min_projected_date']}."
        )

        return {
            "current_cash": results["current_cash"],
            "forecast_df": results["forecast_df"],
            "min_projected_cash": results["min_projected_cash"],
            "min_projected_date": results["min_projected_date"],
            "max_projected_cash": results["max_projected_cash"],
            "final_projected_cash": results["final_projected_cash"],
            "net_projected_change": results["net_projected_change"],
            "pending_receivables": results["pending_receivables"],
            "pending_payables": results["pending_payables"],
            "runway_days": results["runway_days"],
            "forecast_commentary": results["commentary"],
            "agent_logs": logs,
            "errors": errors
        }
    except Exception as e:
        logger.error("Cash Flow Predictor Agent error: %s", e)
        errors.append(f"Cash Flow Predictor error: {str(e)}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Cash Flow Predictor Agent: Error - {str(e)}")
        return {
            "current_cash": 0.0,
            "forecast_df": pd.DataFrame(),
            "min_projected_cash": 0.0,
            "min_projected_date": "N/A",
            "max_projected_cash": 0.0,
            "final_projected_cash": 0.0,
            "net_projected_change": 0.0,
            "pending_receivables": 0.0,
            "pending_payables": 0.0,
            "runway_days": 0,
            "forecast_commentary": "Cash forecast unavailable due to error.",
            "agent_logs": logs,
            "errors": errors
        }


def risk_detector_node(state: FinoraState) -> Dict[str, Any]:
    """Node 3: Execute risk detection and classification."""
    logs = list(state.get("agent_logs", []))
    errors = list(state.get("errors", []))
    logger.info("Executing Node 3: Risk Detector Agent")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Risk Detector Agent: Assessing reserve shortages.")

    try:
        min_reserve = state.get("minimum_reserve", 5000.0)
        results = run_risk_detector(minimum_reserve=min_reserve)

        logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Risk Detector Agent: Overall status: "
            f"[{results['overall_risk_level']}]. {results['risk_days_count']} day(s) below reserve."
        )

        return {
            "overall_risk_level": results["overall_risk_level"],
            "risk_days_count": results["risk_days_count"],
            "earliest_risk_date": results["earliest_risk_date"],
            "earliest_risk_level": results["earliest_risk_level"],
            "earliest_risk_shortage": results["earliest_risk_shortage"],
            "max_shortage": results["max_shortage"],
            "risks": results["risks"],
            "risk_assessment": results["assessment"],
            "agent_logs": logs,
            "errors": errors
        }
    except Exception as e:
        logger.error("Risk Detector Agent error: %s", e)
        errors.append(f"Risk Detector error: {str(e)}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Risk Detector Agent: Error - {str(e)}")
        return {
            "overall_risk_level": "WARNING",
            "risk_days_count": 0,
            "earliest_risk_date": "None",
            "earliest_risk_level": "WARNING",
            "earliest_risk_shortage": 0.0,
            "max_shortage": 0.0,
            "risks": [],
            "risk_assessment": "Risk assessment unavailable due to error.",
            "agent_logs": logs,
            "errors": errors
        }


def strategy_advisor_node(state: FinoraState) -> Dict[str, Any]:
    """Node 4: Execute strategy advisor."""
    logs = list(state.get("agent_logs", []))
    errors = list(state.get("errors", []))
    logger.info("Executing Node 4: Strategy Advisor Agent")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Advisor Agent: Formulating strategic recommendations.")

    try:
        strategies = run_strategy_advisor(
            current_cash=state.get("current_cash"),
            forecast=state.get("forecast_df"),
            risks=state.get("risks"),
            minimum_reserve=state.get("minimum_reserve", 5000.0)
        )

        logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Advisor Agent: Generated "
            f"{len(strategies)} prioritized strategic recommendations."
        )

        return {
            "strategies": strategies,
            "agent_logs": logs,
            "errors": errors
        }
    except Exception as e:
        logger.error("Strategy Advisor Agent error: %s", e)
        errors.append(f"Strategy Advisor error: {str(e)}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Advisor Agent: Error - {str(e)}")
        return {
            "strategies": [
                {
                    "Priority": "MEDIUM",
                    "Area": "System Alert",
                    "Issue": "Strategy engine experienced an error.",
                    "Recommendation": "Verify financial records and database connectivity."
                }
            ],
            "agent_logs": logs,
            "errors": errors
        }


def financial_report_node(state: FinoraState) -> Dict[str, Any]:
    """Node 5: Execute financial report compilation."""
    logs = list(state.get("agent_logs", []))
    errors = list(state.get("errors", []))
    logger.info("Executing Node 5: Financial Report Agent")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Financial Report Agent: Compiling executive report.")

    try:
        report_result = run_financial_report(state)

        logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Financial Report Agent: Executive report "
            f"and downloadable files created successfully."
        )

        return {
            "executive_summary": report_result["executive_summary"],
            "markdown_report": report_result["markdown_report"],
            "text_report": report_result["text_report"],
            "report_timestamp": report_result["timestamp"],
            "agent_logs": logs,
            "errors": errors
        }
    except Exception as e:
        logger.error("Financial Report Agent error: %s", e)
        errors.append(f"Financial Report error: {str(e)}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Financial Report Agent: Error - {str(e)}")
        return {
            "executive_summary": "Report synthesis unavailable.",
            "markdown_report": "# Financial Report\n\nReport generation failed due to an error.",
            "text_report": "Financial Report generation failed.",
            "report_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_logs": logs,
            "errors": errors
        }


# =====================================================================
# COMPILE WORKFLOW GRAPH
# =====================================================================

def build_finora_graph():
    """Build and compile the LangGraph multi-agent workflow."""
    workflow = StateGraph(FinoraState)

    # Register nodes
    workflow.add_node("data_analyst", data_analyst_node)
    workflow.add_node("cash_flow_predictor", cash_flow_predictor_node)
    workflow.add_node("risk_detector", risk_detector_node)
    workflow.add_node("strategy_advisor", strategy_advisor_node)
    workflow.add_node("financial_report", financial_report_node)

    # Define linear execution edge pipeline
    workflow.add_edge(START, "data_analyst")
    workflow.add_edge("data_analyst", "cash_flow_predictor")
    workflow.add_edge("cash_flow_predictor", "risk_detector")
    workflow.add_edge("risk_detector", "strategy_advisor")
    workflow.add_edge("strategy_advisor", "financial_report")
    workflow.add_edge("financial_report", END)

    return workflow.compile()


# Global compiled app
_compiled_app = None


def get_finora_graph():
    """Return the cached compiled LangGraph workflow instance."""
    global _compiled_app
    if _compiled_app is None:
        _compiled_app = build_finora_graph()
    return _compiled_app


def run_multi_agent_system(
    forecast_days: int = 30,
    minimum_reserve: float = 5000.0,
    csv_path: Optional[str] = None
) -> FinoraState:
    """Execute the complete multi-agent workflow end-to-end.

    Args:
        forecast_days: Number of forecast days (e.g. 30).
        minimum_reserve: Minimum cash reserve amount threshold.
        csv_path: Optional path to historical transactions CSV.

    Returns:
        FinoraState: Complete multi-agent state with all intermediate and final outputs.
    """
    logger.info("Initiating FINORA AI Multi-Agent Orchestration Pipeline...")
    graph = get_finora_graph()

    initial_state: FinoraState = {
        "forecast_days": forecast_days,
        "minimum_reserve": minimum_reserve,
        "csv_path": csv_path,
        "agent_logs": [],
        "errors": []
    }

    final_state = graph.invoke(initial_state)
    logger.info("Multi-Agent Orchestration Pipeline finished successfully.")
    return final_state


if __name__ == "__main__":
    final_output = run_multi_agent_system(forecast_days=30, minimum_reserve=5000.0)

    print("\n" + "=" * 60)
    print("FINORA AI - MULTI-AGENT ORCHESTRATION PIPELINE COMPLETE")
    print("=" * 60)
    print("Agent Logs:")
    for entry in final_output.get("agent_logs", []):
        print(" ", entry)

    print("\nExecutive Summary:")
    print(final_output.get("executive_summary"))

    print("\nOverall Risk:", final_output.get("overall_risk_level"))
    print("Strategies Count:", len(final_output.get("strategies", [])))
    print("Errors:", final_output.get("errors"))

