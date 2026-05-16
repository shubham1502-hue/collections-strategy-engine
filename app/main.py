import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Collections Strategy Engine", layout="wide")

st.title("Collections Strategy Engine - A/B Test Dashboard")

st.markdown("""
This dashboard compares a **Model-Driven (Treatment)** contact strategy against a **Flat (Control)** strategy.
""")

@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_path = os.path.join(base_path, "data", "processed", "ab_test_summary.csv")
    dpd_path = os.path.join(base_path, "outputs", "recovery_by_dpd.csv")
    channel_path = os.path.join(base_path, "outputs", "channel_performance.csv")
    pareto_path = os.path.join(base_path, "outputs", "pareto_segments.csv")
    
    summary = pd.read_csv(summary_path) if os.path.exists(summary_path) else None
    dpd = pd.read_csv(dpd_path) if os.path.exists(dpd_path) else None
    channel = pd.read_csv(channel_path) if os.path.exists(channel_path) else None
    pareto = pd.read_csv(pareto_path) if os.path.exists(pareto_path) else None
    
    return summary, dpd, channel, pareto

summary, dpd, channel, pareto = load_data()

if summary is not None:
    st.header("Executive Summary")
    
    control = summary[summary["arm"] == "Control"].iloc[0]
    treatment = summary[summary["arm"] == "Treatment"].iloc[0]
    
    lift_rr = treatment["actual_response_rate_pct"] - control["actual_response_rate_pct"]
    lift_recovery = ((treatment["total_recovered_inr"] / control["total_recovered_inr"]) - 1) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Response Rate (Treatment)", f"{treatment['actual_response_rate_pct']:.2f}%", f"+{lift_rr:.2f} pp")
    col2.metric("Response Rate (Control)", f"{control['actual_response_rate_pct']:.2f}%")
    col3.metric("Total Recovery (Treatment)", f"₹ {treatment['total_recovered_inr']:,.0f}", f"+{lift_recovery:.2f}%")
    col4.metric("Total Recovery (Control)", f"₹ {control['total_recovered_inr']:,.0f}")
    
st.divider()

col_left, col_right = st.columns(2)

with col_left:
    if dpd is not None:
        st.subheader("Recovery by DPD Bucket")
        st.dataframe(dpd, use_container_width=True)

with col_right:
    if channel is not None:
        st.subheader("Channel Performance (Treatment)")
        st.dataframe(channel, use_container_width=True)

if pareto is not None:
    st.subheader("Top Recovery Segments (Pareto)")
    st.dataframe(pareto, use_container_width=True)
