"""FINORA AI - AI-Powered Financial Decision-Support System for Small Businesses.

Multi-Agent Architecture powered by LangGraph, Pandas, OpenPyXL, and OpenRouter AI.
"""

from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.excel_manager import (
    EXCEL_FILE,
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

from agents.data_analyst import run_data_analyst
from agents.cash_flow_predictor import run_cash_flow_predictor
from agents.risk_detector_agent import run_risk_detector
from agents.strategy_advisor import run_strategy_advisor
from agents.financial_report_agent import run_financial_report
from agents.orchestrator import run_multi_agent_system
from utils.gemini_client import get_gemini_client

# =====================================================================
# 1. PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="FINORA AI - Financial Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean UI styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 10px;
    }

    .agent-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 5px;
    }

    .agent-pill-active {
        background-color: #e8f5e9;
        color: #2e7d32;
    }

    .agent-pill-offline {
        background-color: #fff3e0;
        color: #e65100;
    }

    .priority-high {
        border-left: 5px solid #d32f2f;
        background-color: #ffebee;
    }

    .priority-medium {
        border-left: 5px solid #f57c00;
        background-color: #fff8e1;
    }

    .priority-normal {
        border-left: 5px solid #388e3c;
        background-color: #e8f5e9;
    }

    /* FINORA AI LANDING PAGE */

    .finora-hero {
        background: linear-gradient(135deg, #0C182D, #183B50);
        padding: 55px 40px;
        border-radius: 18px;
        border: 1px solid #24566A;
        margin: 10px 0 25px 0;
    }

    .finora-hero h1 {
        color: #FFFFFF;
        font-size: 48px;
        font-weight: 800;
    }

    .finora-hero h3 {
        color: #22D3BE;
        font-size: 23px;
    }

    .finora-hero p {
        color: #D5E2ED;
        font-size: 17px;
    }

    .finora-feature {
        background: #F1F7F8;
        color: #15283D;
        padding: 22px;
        border-radius: 12px;
        min-height: 150px;
        border-top: 4px solid #22D3BE;
    }

</style>
""", unsafe_allow_html=True)


# =====================================================================
# 2. DATABASE INTEGRITY CHECK & GLOBAL DATA LOADING
# =====================================================================
if not Path(EXCEL_FILE).exists():
    st.error("Excel database not found. Please verify finora_data.xlsx in data folder.")
    st.stop()

# Load Database sheets
try:
    business = get_business()
    transactions = get_transactions()
    receivables = get_receivables()
    payables = get_payables()
    settings_df = get_settings()

    # Dynamic settings extraction with robust fallbacks
    min_reserve = 5000.0
    default_forecast_days = 30
    if not settings_df.empty and "Setting" in settings_df.columns:
        res_row = settings_df[settings_df["Setting"] == "Minimum Cash Reserve"]
        if not res_row.empty:
            min_reserve = float(res_row.iloc[0]["Value"])
        fc_row = settings_df[settings_df["Setting"] == "Forecast Days"]
        if not fc_row.empty:
            default_forecast_days = int(fc_row.iloc[0]["Value"])

    # Cash Calculation
    opening_cash = float(business.iloc[0]["Opening Cash"]) if not business.empty else 0.0

    if not transactions.empty and "Type" in transactions.columns and "Amount" in transactions.columns:
        income = float(transactions.loc[transactions["Type"] == "Income", "Amount"].sum())
        expenses = float(transactions.loc[transactions["Type"] == "Expense", "Amount"].sum())
    else:
        income = 0.0
        expenses = 0.0

    current_cash = opening_cash + income - expenses
    business_name = business.iloc[0]["Business Name"] if not business.empty else "Business Enterprise"

except Exception as e:
    st.error(f"Error loading business database: {e}")
    st.stop()


# =====================================================================
# 3. SIDEBAR NAVIGATION & SYSTEM STATUS
# =====================================================================
st.sidebar.title("💰 FINORA AI")
st.sidebar.caption("Multi-Agent Financial Intelligence")
st.sidebar.markdown(f"**Enterprise:** {business_name}")

gemini_client = get_gemini_client()
if gemini_client.is_available:
    st.sidebar.markdown(
        '<span class="agent-pill agent-pill-active">● Gemini AI Connected</span>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<span class="agent-pill agent-pill-offline">○ Gemini Offline (Fallback Active)</span>',
        unsafe_allow_html=True
    )

st.sidebar.divider()
# Set the default page
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# Navigate to dashboard
def go_to_dashboard():
    st.session_state["page"] = "Business Overview"

page = st.sidebar.radio(
    "FINANCIAL SUITE",
    [
        "Home",
        "Business Overview",
        "Transaction Management",
        "Historical Financial Analysis",
        "Cash Flow Forecast",
        "Cash Flow Risk Analysis",
        "Strategy Advisor",
        "Financial Reports",
        "AI Agent Centre"
    ],
    key="page"
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **Architecture Guarantee**\n"
    "All numerical totals and forecasts are deterministic Python calculations. "
    "Gemini is used solely for narrative explanations."
)


# =====================================================================
# HOME: FINORA AI LANDING PAGE
# =====================================================================
if page == "Home":
    st.markdown("""
    <div class="finora-hero">
        <h3>INTELLIGENCE BEHIND EVERY FINANCIAL DECISION</h3>
        <h1>FINORA AI</h1>
        <p>
            Smarter cash-flow management for small businesses.
            Analyze financial data, forecast future cash positions,
            detect risks early, and make informed financial decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    intro_col, visual_col = st.columns([1.15, 0.85], gap="large")

    with intro_col:
        st.subheader("Take control of your business finances.")
        st.write(
            "FINORA AI is an AI-powered financial decision-support system "
            "designed to help small businesses understand their cash flow, "
            "prepare for upcoming obligations, and identify possible "
            "liquidity problems before they happen."
        )
        st.button(
            "🚀 Get Started",
            type="primary",
            use_container_width=True,
            on_click=go_to_dashboard
        )

    with visual_col:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, #10243A, #1B5260);
            color: white;
            padding: 28px;
            border-radius: 16px;
            min-height: 235px;
            border: 1px solid #2B7180;">
            <div style="color:#22D3BE;font-size:14px;font-weight:700;">
                FINANCIAL INTELLIGENCE
            </div>
            <div style="font-size:25px;font-weight:750;margin-top:14px;">
                See risks earlier.<br>Decide smarter.
            </div>
            <div style="color:#D5E2ED;margin-top:14px;font-size:15px;">
                Financial analysis · Cash forecasting · Risk detection
            </div>
            <div style="
                margin-top:24px;
                height:7px;
                border-radius:10px;
                background:linear-gradient(90deg,#22D3BE 0 72%,#477080 72% 100%);">
            </div>
            <div style="color:#B9D0D8;font-size:12px;margin-top:8px;">
                ANALYZE  •  PREDICT  •  PROTECT
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.header("What FINORA AI can do")

    feature_cols = st.columns(3, gap="medium")
    feature_cards = [
        (
            "📊 Financial Analysis",
            "Understand income, expenses, transaction history, and business performance."
        ),
        (
            "📈 Cash Flow Prediction",
            "Project future cash balances using upcoming inflows and outflows."
        ),
        (
            "🛡️ Early Risk Detection",
            "Identify projected cash shortages and minimum-reserve breaches."
        )
    ]

    for column, (heading, description) in zip(feature_cols, feature_cards):
        with column:
            st.markdown(
                f"""
                <div class="finora-feature">
                    <h4>{heading}</h4>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()
    st.header("Powered by five specialist agents")

    agent_cols = st.columns(5)
    agent_names = [
        "Data Analyst",
        "Cash Flow Predictor",
        "Risk Detector",
        "Strategy Advisor",
        "Financial Report"
    ]
    for column, agent_name in zip(agent_cols, agent_names):
        with column:
            st.markdown(f"**🤖 {agent_name} Agent**")

    st.caption(
        "FINORA AI combines Python-based financial calculations with "
        "AI-generated explanations to support better business decisions."
    )

# =====================================================================
# PAGE 1: BUSINESS OVERVIEW
# =====================================================================
elif page == "Business Overview":
    st.title("💼 Business Overview")
    st.caption(f"Financial summary and liquidity status for {business_name}")
    st.divider()

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Available Cash", f"₹{current_cash:,.2f}")
    col2.metric("Total Income", f"₹{income:,.2f}")
    col3.metric("Total Expenses", f"₹{expenses:,.2f}")
    net_current = income - expenses
    col4.metric(
        "Net Operating Movement",
        f"₹{net_current:,.2f}",
        delta=f"{'+' if net_current >= 0 else ''}{net_current:,.2f}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Secondary row: Pending receivables and payables
    col_a, col_b, col_c = st.columns(3)
    pending_rec_amt = 0.0
    if not receivables.empty and "Status" in receivables.columns:
        p_rec = receivables[receivables["Status"].astype(str).str.lower() == "pending"]
        pending_rec_amt = float(pd.to_numeric(p_rec["Amount"], errors="coerce").fillna(0).sum())

    pending_pay_amt = 0.0
    if not payables.empty and "Status" in payables.columns:
        p_pay = payables[payables["Status"].astype(str).str.lower() == "pending"]
        pending_pay_amt = float(pd.to_numeric(p_pay["Amount"], errors="coerce").fillna(0).sum())

    col_a.metric("Minimum Reserve Required", f"₹{min_reserve:,.2f}")
    col_b.metric("Pending Customer Inflows", f"₹{pending_rec_amt:,.2f}")
    col_c.metric("Pending Supplier Outflows", f"₹{pending_pay_amt:,.2f}")

    st.divider()

    # Ledger Snapshot
    st.subheader("📋 Recent Transaction Ledger")
    if transactions.empty:
        st.info("No transactions logged in the database yet.")
    else:
        st.dataframe(transactions.tail(10), use_container_width=True)

    st.caption("Showing the 10 most recent transactions from finora_data.xlsx.")


# =====================================================================
# PAGE 2: TRANSACTION MANAGEMENT
# =====================================================================
elif page == "Transaction Management":
    st.title("📑 Transaction Management")
    st.caption("Record new income/expenses and inspect full ledger history.")
    st.divider()

    tab1, tab2 = st.tabs(["➕ Add New Transaction", "📜 Transaction History"])

    with tab1:
        st.subheader("Record Transaction")
        with st.form("transaction_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                t_date = st.date_input("Transaction Date")
                t_type = st.selectbox("Transaction Type", ["Income", "Expense"])
                t_category = st.selectbox(
                    "Category",
                    [
                        "Sales",
                        "Customer Payment",
                        "Supplier Payment",
                        "Rent",
                        "Salary",
                        "Electricity",
                        "Marketing",
                        "Operations",
                        "Other"
                    ]
                )
            with f_col2:
                t_description = st.text_input("Description", placeholder="e.g. Bulk inventory supply")
                t_amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)

            submitted = st.form_submit_button("💾 Save Transaction to Excel")

            if submitted:
                if not t_description.strip():
                    st.error("Please provide a valid description.")
                else:
                    try:
                        add_transaction(t_date, t_description, t_type, t_category, t_amount)
                        st.success("✅ Transaction saved successfully to finora_data.xlsx!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Failed to record transaction: {err}")

    with tab2:
        st.subheader("Complete Transaction History")
        if transactions.empty:
            st.info("No transactions recorded yet.")
        else:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                type_filter = st.multiselect(
                    "Filter by Type",
                    options=list(transactions["Type"].unique()),
                    default=list(transactions["Type"].unique())
                )
            with filter_col2:
                cat_filter = st.multiselect(
                    "Filter by Category",
                    options=list(transactions["Category"].unique()),
                    default=list(transactions["Category"].unique())
                )

            filtered_df = transactions[
                (transactions["Type"].isin(type_filter)) &
                (transactions["Category"].isin(cat_filter))
            ]

            st.dataframe(filtered_df, use_container_width=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Filtered Records", len(filtered_df))
            f_in = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum() if not filtered_df.empty else 0
            f_out = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum() if not filtered_df.empty else 0
            m2.metric("Filtered Inflows", f"₹{f_in:,.2f}")
            m3.metric("Filtered Outflows", f"₹{f_out:,.2f}")


# =====================================================================
# PAGE 3: HISTORICAL FINANCIAL ANALYSIS
# =====================================================================
elif page == "Historical Financial Analysis":
    st.title("📊 Historical Financial Analysis")
    st.caption("Deep-dive transaction analytics, departmental spending breakdown, and budget variances.")
    st.divider()

    csv_path = Path(__file__).resolve().parent / "data" / "cash_flow_transactions.csv"

    if not csv_path.exists():
        st.error("Historical dataset (cash_flow_transactions.csv) not found in data directory.")
    else:
        try:
            # Run Data Analyst Agent
            data_agent_result = run_data_analyst(file_path=csv_path)

            # Natural-Language Insights Banner
            st.info(f"🤖 **Data Analyst Agent Insights:**\n\n{data_agent_result['insights']}")
            st.divider()

            # Top Level Metrics (Labeled as Dataset Amounts, without ₹)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Historical Transactions", data_agent_result["total_transactions"])
            c2.metric("Total Historical Inflow", f"{data_agent_result['total_income']:,.2f} [Dataset Amount]")
            c3.metric("Total Historical Outflow", f"{data_agent_result['total_expenses']:,.2f} [Dataset Amount]")
            c4.metric("Net Historical Cash Flow", f"{data_agent_result['net_cash_flow']:,.2f} [Dataset Amount]")

            st.markdown("<br>", unsafe_allow_html=True)

            # Visualizations
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("📈 Monthly Cash Inflow vs Outflow")
                monthly_data = data_agent_result["monthly_analysis"].reset_index()
                fig_monthly = px.bar(
                    monthly_data,
                    x="Month",
                    y=["Cash Inflow", "Cash Outflow"],
                    barmode="group",
                    title="Monthly Cash Movement (Dataset Amounts)",
                    color_discrete_map={"Cash Inflow": "#2E7D32", "Cash Outflow": "#C62828"}
                )
                fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Amount (Dataset Units)", legend_title="")
                st.plotly_chart(fig_monthly, use_container_width=True)

            with col_chart2:
                st.subheader("🏢 Department-wise Expenditure")
                dept_series = data_agent_result["department_expenses"].reset_index()
                dept_series.columns = ["Department", "Outflow"]
                fig_dept = px.bar(
                    dept_series,
                    x="Department",
                    y="Outflow",
                    title="Department Expenses (Dataset Amounts)",
                    color="Outflow",
                    color_continuous_scale="Reds"
                )
                fig_dept.update_layout(xaxis_title="Department", yaxis_title="Total Outflow (Dataset Units)")
                st.plotly_chart(fig_dept, use_container_width=True)

            st.divider()

            # Budget Analysis
            st.subheader("🎯 Budget Variance Analysis")
            b1, b2, b3 = st.columns(3)
            b1.metric("Allocated Budget", f"{data_agent_result['total_budget']:,.2f} [Dataset Amount]")
            b2.metric("Actual Expenditure", f"{data_agent_result['actual_expenses']:,.2f} [Dataset Amount]")
            diff = data_agent_result["budget_difference"]
            b3.metric(
                "Budget Difference",
                f"{diff:,.2f} [Dataset Amount]",
                delta=f"{'+' if diff >= 0 else ''}{diff:,.2f}",
                delta_color="normal" if diff >= 0 else "inverse"
            )

        except Exception as e:
            st.error(f"Error during historical analysis: {e}")


# =====================================================================
# PAGE 4: CASH FLOW FORECAST
# =====================================================================
elif page == "Cash Flow Forecast":
    st.title("📈 Cash Flow Forecast")
    st.caption("Deterministic 30-day forward cash projection powered by Cash Flow Predictor Agent.")
    st.divider()

    horizon_col, _ = st.columns([2, 4])
    with horizon_col:
        selected_horizon = st.slider("Select Forecast Horizon (Days)", min_value=15, max_value=60, value=default_forecast_days, step=5)

    try:
        # Run Cash Flow Predictor Agent
        predictor_result = run_cash_flow_predictor(forecast_days=selected_horizon)

        # AI Commentary Card
        st.info(f"🤖 **Cash Flow Predictor Commentary:**\n\n{predictor_result['commentary']}")

        # Forecast KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Current Balance", f"₹{predictor_result['current_cash']:,.2f}")
        k2.metric("Lowest Projected Balance", f"₹{predictor_result['min_projected_cash']:,.2f}")
        k3.metric("Lowest Liquidity Date", predictor_result['min_projected_date'])
        k4.metric("30-Day Net Change", f"₹{predictor_result['net_projected_change']:,.2f}")

        st.divider()

        # Interactive Trajectory Chart
        st.subheader(f"📊 {selected_horizon}-Day Cash Projection Trajectory")
        f_df = predictor_result["forecast_df"].copy()
        f_df["Date"] = pd.to_datetime(f_df["Date"])

        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=f_df["Date"],
            y=f_df["Projected Cash"],
            mode="lines+markers",
            name="Projected Cash",
            line=dict(color="#1976D2", width=3)
        ))
        # Add Minimum Reserve threshold line
        fig_forecast.add_hline(
            y=min_reserve,
            line_dash="dash",
            line_color="#E53935",
            annotation_text=f"Min Reserve Threshold (₹{min_reserve:,.0f})",
            annotation_position="bottom right"
        )
        fig_forecast.update_layout(
            title=f"Projected Cash Balance vs. Minimum Reserve Threshold",
            xaxis_title="Date",
            yaxis_title="Cash Balance (₹)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        st.divider()

        # Detailed Daily Forecast Table with CSV Download
        st.subheader("📅 Daily Cash Inflow, Outflow & Projected Balance")
        st.dataframe(f_df, use_container_width=True)

        csv_download = f_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Daily Forecast (CSV)",
            data=csv_download,
            file_name=f"finora_cash_flow_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error executing Cash Flow Forecast: {e}")


# =====================================================================
# PAGE 5: CASH FLOW RISK ANALYSIS
# =====================================================================
elif page == "Cash Flow Risk Analysis":
    st.title("🚨 Cash Flow Risk Analysis")
    st.caption("Early detection of reserve shortages and insolvency threats before they materialize.")
    st.divider()

    try:
        # Run Risk Detector Agent
        risk_result = run_risk_detector(minimum_reserve=min_reserve)

        # Prominent Risk Status Banner
        r_level = risk_result["overall_risk_level"]
        if r_level == "CRITICAL":
            st.error("🚨 **CRITICAL RISK DETECTED**: Cash balance is projected to turn negative during the forecast horizon.")
        elif r_level == "WARNING":
            st.warning("⚠️ **WARNING**: Projected cash balance falls below the established minimum reserve threshold.")
        else:
            st.success("✅ **NORMAL**: Cash reserves remain above the minimum required threshold throughout the forecast period.")

        st.info(f"🤖 **Risk Detector Agent Assessment:**\n\n{risk_result['assessment']}")

        # Risk Metrics Row
        rk1, rk2, rk3, rk4 = st.columns(4)
        rk1.metric("Overall Risk Status", r_level)
        rk2.metric("Total Days at Risk", risk_result["risk_days_count"])
        rk3.metric("Earliest Risk Date", risk_result["earliest_risk_date"])
        rk4.metric("Maximum Reserve Shortage", f"₹{risk_result['max_shortage']:,.2f}")

        st.divider()

        # Detailed Risk Breaches Table
        st.subheader("📋 Detected Cash Reserve Breaches")
        if not risk_result["risks"]:
            st.success("No reserve shortages or insolvency events detected in the projection.")
        else:
            risks_table = pd.DataFrame(risk_result["risks"])
            risks_table["Date"] = pd.to_datetime(risks_table["Date"]).dt.strftime("%Y-%m-%d")
            st.dataframe(risks_table, use_container_width=True)

        st.divider()

        # Risk Trajectory Chart
        st.subheader("📉 Liquidity Deficit Visualization")
        forecast_risk = risk_result["forecast_df"].copy()
        fig_risk = px.area(
            forecast_risk,
            x="Date",
            y="Projected Cash",
            title="Projected Cash Flow with Reserve Boundary",
            color_discrete_sequence=["#EF5350" if r_level != "NORMAL" else "#66BB6A"]
        )
        fig_risk.add_hline(y=min_reserve, line_dash="dash", line_color="black", annotation_text="Reserve Baseline")
        st.plotly_chart(fig_risk, use_container_width=True)

    except Exception as e:
        st.error(f"Error during Risk Analysis: {e}")


# =====================================================================
# PAGE 6: STRATEGY ADVISOR
# =====================================================================
elif page == "Strategy Advisor":
    st.title("💡 Strategy Advisor")
    st.caption("Evidence-based financial strategies and actionable risk mitigations.")
    st.divider()

    try:
        # Run Strategy Advisor Agent
        strategies = run_strategy_advisor(minimum_reserve=min_reserve)

        st.subheader("🎯 Prioritized Action Plan")
        st.write(f"Generated **{len(strategies)} strategic recommendations** based on current ledger, pending receivables, and upcoming obligations.")

        for idx, strat in enumerate(strategies, start=1):
            prio = strat.get("Priority", "MEDIUM")
            prio_class = "priority-high" if prio == "HIGH" else ("priority-medium" if prio == "MEDIUM" else "priority-normal")

            with st.container():
                st.markdown(f"""
                <div class="metric-card {prio_class}">
                    <span style="float: right; font-weight: 700;">Priority: {prio}</span>
                    <h4 style="margin: 0; color: #1a237e;">Strategy {idx}: {strat.get('Area')}</h4>
                    <p style="margin-top: 8px; margin-bottom: 4px;"><strong>Identified Issue:</strong> {strat.get('Issue')}</p>
                    <p style="margin: 0;"><strong>Action Recommendation:</strong> {strat.get('Recommendation')}</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error executing Strategy Advisor: {e}")


# =====================================================================
# PAGE 7: FINANCIAL REPORTS
# =====================================================================
elif page == "Financial Reports":
    st.title("📑 Financial Reports")
    st.caption("Consolidated business financial briefing synthesized by Financial Report Agent.")
    st.divider()

    try:
        # Run LangGraph Orchestrator or assemble current state
        with st.spinner("Compiling latest multi-agent financial report..."):
            pipeline_state = run_multi_agent_system(
                forecast_days=default_forecast_days,
                minimum_reserve=min_reserve
            )

        # Executive Summary Box
        st.subheader("Executive Briefing")
        st.info(pipeline_state.get("executive_summary", "Summary unavailable."))

        st.divider()

        # Key Financial Summary Table
        st.subheader("Key Business Performance Snapshot")
        snap_col1, snap_col2, snap_col3 = st.columns(3)
        snap_col1.metric("Available Cash", f"₹{pipeline_state.get('current_cash', 0.0):,.2f}")
        snap_col2.metric("Overall Risk Status", pipeline_state.get("overall_risk_level", "NORMAL"))
        snap_col3.metric("Lowest Projected Balance", f"₹{pipeline_state.get('min_projected_cash', 0.0):,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Download Report Buttons
        st.subheader("📥 Download Financial Report")
        d_col1, d_col2 = st.columns(2)

        md_content = pipeline_state.get("markdown_report", "")
        text_content = pipeline_state.get("text_report", "")
        report_timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        with d_col1:
            st.download_button(
                label="📄 Download Report as Markdown (.md)",
                data=md_content,
                file_name=f"FINORA_Financial_Report_{report_timestamp_str}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with d_col2:
            st.download_button(
                label="📄 Download Report as Plain Text (.txt)",
                data=text_content,
                file_name=f"FINORA_Financial_Report_{report_timestamp_str}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()

        # Full Rendered Markdown Report Preview
        with st.expander("👁️ View Full Formatted Report", expanded=True):
            st.markdown(md_content)

    except Exception as e:
        st.error(f"Error compiling Financial Report: {e}")


# =====================================================================
# PAGE 8: AI AGENT CENTRE
# =====================================================================
elif page == "AI Agent Centre":
    st.title("🤖 AI Agent Centre")
    st.caption("Multi-agent orchestration console powered by LangGraph.")
    st.divider()

    # System Status Bar
    st.subheader("System & Model Architecture Status")
    stat_col1, stat_col2, stat_col3 = st.columns(3)

    stat_col1.markdown("""
    **Multi-Agent Orchestrator:**  
    `LangGraph StateGraph` (Compiled)
    """)

    gemini_stat = "Connected (Gemini 2.5/2.0 Flash)" if gemini_client.is_available else "Offline Mode (Deterministic Templates)"
    stat_col2.markdown(f"""
    **Natural-Language Insight Engine:**  
    `{gemini_stat}`
    """)

    stat_col3.markdown("""
    **Financial Calculation Engine:**  
    `Pandas & NumPy` (100% Deterministic)
    """)

    st.divider()

    # Specialist Agent Directory
    st.subheader("Specialist Agents in Workflow")
    agents_info = [
        ("1. Data Analyst Agent", "Historical transactions, monthly grouping, departmental spending, budget variances.", "Pandas, modules.financial_analyzer"),
        ("2. Cash Flow Predictor Agent", "30-day cumulative forward cash forecast, receivable/payable integration.", "NumPy, modules.forecast_engine"),
        ("3. Risk Detector Agent", "Reserve shortfall detection, insolvency prediction, risk level classification.", "modules.risk_detector"),
        ("4. Strategy Advisor Agent", "Prioritized evidence-based financial action cards and risk mitigations.", "agents.strategy_advisor"),
        ("5. Financial Report Agent", "Executive briefing synthesis, downloadable Markdown and plain-text reports.", "agents.financial_report_agent")
    ]

    for name, desc, tech in agents_info:
        st.markdown(f"""
        - **{name}**: {desc} *(Engine: `{tech}`)*
        """)

    st.divider()

    # Interactive Multi-Agent Execution Console
    st.subheader("Multi-Agent Workflow Execution Console")
    st.write("Trigger the complete LangGraph state progression across all 5 specialist agents in real-time.")

    run_pipeline = st.button("🚀 Execute Complete Multi-Agent Workflow", type="primary")

    if run_pipeline:
        progress_bar = st.progress(0, text="Initializing LangGraph Orchestration Pipeline...")
        try:
            progress_bar.progress(20, text="Node 1: Data Analyst Agent executing...")
            # Run LangGraph pipeline
            final_state = run_multi_agent_system(
                forecast_days=default_forecast_days,
                minimum_reserve=min_reserve
            )
            progress_bar.progress(100, text="Multi-Agent Pipeline completed successfully!")

            st.success("✅ Multi-Agent Orchestration Workflow completed with 0 errors!")

            # Execution Audit Logs
            st.subheader("📜 Agent Execution Audit Logs")
            for log in final_state.get("agent_logs", []):
                st.code(log, language="bash")

            # Final Executive Summary
            st.subheader("Synthesized Executive Summary")
            st.info(final_state.get("executive_summary"))

        except Exception as e:
            st.error(f"Error during multi-agent workflow execution: {e}")
