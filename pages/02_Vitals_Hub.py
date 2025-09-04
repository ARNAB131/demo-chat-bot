# pages/02_Vitals_Hub.py
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from vitals_bridge import set_latest_vitals

st.set_page_config(page_title="Vitals Hub", page_icon="💓", layout="centered")
st.title("💓 Vitals Hub")
st.caption("Prepare or import recent vitals so the chat bot can attach them to your appointment.")

st.subheader("1) Create or Upload Vitals")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("Generate sample vitals (100 rows)")
with col2:
    uploaded = st.file_uploader("Upload CSV with columns: timestamp, systolic_bp, diastolic_bp, body_temperature", type=["csv"])

df = st.session_state.get("forecast_data", pd.DataFrame())

if gen:
    now = datetime.now()
    ts = pd.date_range(end=now, periods=100, freq="5min")
    syst = np.clip(120 + np.random.randn(100)*5, 100, 150).round(1)
    diast = np.clip(80 + np.random.randn(100)*3, 60, 100).round(1)
    temp = np.clip(36.7 + np.random.randn(100)*0.2, 36.0, 38.0).round(1)
    df = pd.DataFrame({
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "systolic_bp": syst,
        "diastolic_bp": diast,
        "body_temperature": temp,
    })
    st.session_state["forecast_data"] = df

if uploaded is not None:
    try:
        df_up = pd.read_csv(uploaded)
        st.session_state["forecast_data"] = df_up
        df = df_up
        st.success("Vitals CSV loaded into session.")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")

if not df.empty:
    st.dataframe(df.tail(10), use_container_width=True)
    last = df.iloc[-1].to_dict()
    st.write("**Most recent vitals:**", last)

    if st.button("✅ Publish these as 'recent vitals' for the chat bot"):
        vitals_dict = {
            "timestamp": str(last.get("timestamp", datetime.now().isoformat())),
            "systolic_bp": float(last.get("systolic_bp", 120)),
            "diastolic_bp": float(last.get("diastolic_bp", 80)),
            "body_temperature": float(last.get("body_temperature", 36.8)),
        }
        set_latest_vitals(vitals_dict)
        st.success("Recent vitals published! Go back to the chat to attach them (answer Yes).")
else:
    st.info("Generate or upload vitals above to get started.")
