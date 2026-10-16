import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.banking_model import analyze_banking_stress_and_anomalies

st.set_page_config(page_title="Banking & Financial Stress Malaysia", layout="wide")
st.title("BANKING & FINANCIAL STRESS ANALYZER")
st.caption("Credit Growth Anomaly Detection & Yield Spreads (Tables 4.3, 4.4, 4.6)")

z_thresh = st.slider("Anomaly Z-Score Cutoff", 0.8, 2.5, 1.35, 0.05)
stress_list, df_yields, kpis = analyze_banking_stress_and_anomalies(z_thresh)
df_stress = pd.DataFrame([s.model_dump() for s in stress_list])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Gross Impaired Loans Ratio", f"{kpis['gross_impaired_loans_ratio_pct']:.1f}%")
k2.metric("Household Debt to GDP", f"{kpis['household_debt_to_gdp_pct']:.1f}% (DSR: 32.1%)")
k3.metric("5Y AAA Spread (Jul '26)", f"{kpis['aaa_5y_spread_bps']:.0f} bps")
k4.metric("5Y BBB Spread (Jul '26)", f"{kpis['bbb_5y_spread_bps']:.0f} bps")

c1, c2 = st.columns(2)
with c1:
    fig1 = go.Figure(go.Bar(
        x=df_stress["z_score"],
        y=df_stress["sector"],
        orientation="h",
        marker_color=["#D92B2B" if anom else "#1D4ED8" for anom in df_stress["is_anomaly"]]
    ))
    fig1.update_layout(title="Credit Growth Anomaly Z-Score (Red = Anomaly)", paper_bgcolor="#FFFFFF")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    months = ["jan_2026", "feb_2026", "mar_2026", "apr_2026", "may_2026", "jun_2026", "jul_2026"]
    fig2 = go.Figure()
    for _, r in df_yields.iterrows():
        fig2.add_trace(go.Scatter(x=months, y=[float(r[m]) for m in months], mode="lines+markers", name=str(r["instrument"])))
    fig2.update_layout(title="MGS & Corporate Bond Yields 2026", paper_bgcolor="#FFFFFF")
    st.plotly_chart(fig2, use_container_width=True)

st.dataframe(df_stress, use_container_width=True)
