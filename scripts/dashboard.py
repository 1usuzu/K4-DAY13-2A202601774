import streamlit as st
import pandas as pd
import json
from pathlib import Path
import time
from collections import Counter

# Set page layout to wide
st.set_page_config(layout="wide", page_title="AI Observability Dashboard")

# Refresh button and auto refresh hint
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("Day 13 AI Observability Dashboard")
with col_refresh:
    st.write("Auto-refresh every 30s")
    if st.button("Manual Refresh"):
        st.rerun()

# Read logs
log_file = Path("data/logs.jsonl")
if not log_file.exists():
    st.error("Log file not found. Run load test first.")
    st.stop()

data = []
with open(log_file, "r") as f:
    for line in f:
        try:
            data.append(json.loads(line))
        except:
            pass

if not data:
    st.warning("No data in logs yet.")
    st.stop()

df = pd.DataFrame(data)

# Default time range: 1 hour (60 minutes) as per dashboard-spec.md
time_range_min = 60
st.subheader(f"Data for last {time_range_min} minutes")

# Filter data for last 60 minutes if timestamp exists
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=time_range_min)
    try:
        # Assuming logs are in UTC, naive comparison might fail so try localizing
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
        df = df[df["timestamp"] >= cutoff]
    except Exception as e:
        st.warning(f"Time filter skipped: {e}")

# Layout: 6 main panels (2 rows, 3 columns)
col1, col2, col3 = st.columns(3)
st.write("---")
col4, col5, col6 = st.columns(3)

# 1. Latency (events: response_sent, fields: latency_ms)
df_resp = df[df.get("event") == "response_sent"]
if "latency_ms" in df_resp.columns:
    p50 = df_resp["latency_ms"].quantile(0.50)
    p95 = df_resp["latency_ms"].quantile(0.95)
    p99 = df_resp["latency_ms"].quantile(0.99)
    with col1:
        st.metric("Latency P95 (ms)", f"{p95:.0f}" if pd.notna(p95) else "N/A", delta="SLO <= 3000", delta_color="inverse")
        st.caption(f"P50: {p50:.0f} ms | P99: {p99:.0f} ms")
else:
    with col1:
        st.metric("Latency P95 (ms)", "N/A")

# 2. Traffic
df_req = df[df.get("event") == "request_received"]
traffic_count = len(df_req)
rate = traffic_count / time_range_min
with col2:
    st.metric("Traffic Rate (req/min)", f"{rate:.1f}", delta="Threshold >= 1", delta_color="normal")
    st.caption(f"Total Requests: {traffic_count}")

# 3. Errors
df_err = df[df.get("event") == "request_failed"]
err_count = len(df_err)
err_rate = (err_count / traffic_count * 100) if traffic_count > 0 else 0
with col3:
    st.metric("Error Rate (%)", f"{err_rate:.2f}%", delta="SLO <= 2%", delta_color="inverse")
    if err_count > 0 and "error_type" in df_err.columns:
        breakdown = dict(Counter(df_err["error_type"].dropna()))
        st.caption(f"Breakdown: {breakdown}")
    else:
        st.caption("No errors logged")

# 4. Cost
if "cost_usd" in df_resp.columns:
    total_cost = df_resp["cost_usd"].sum()
    with col4:
        st.metric("Total Cost (USD)", f"${total_cost:.4f}", delta="SLO <= 2.5", delta_color="inverse")
else:
    with col4:
        st.metric("Total Cost (USD)", "N/A")

# 5. Tokens
if "tokens_in" in df_resp.columns and "tokens_out" in df_resp.columns:
    tot_in = df_resp["tokens_in"].sum()
    tot_out = df_resp["tokens_out"].sum()
    with col5:
        st.metric("Total Tokens", f"{tot_in + tot_out}", delta="Threshold <= 50000", delta_color="inverse")
        st.caption(f"Tokens In: {tot_in} | Tokens Out: {tot_out}")
else:
    with col5:
        st.metric("Total Tokens", "N/A")

# 6. Quality
if "quality_score" in df_resp.columns:
    q_avg = df_resp["quality_score"].mean()
    with col6:
        st.metric("Quality Proxy (score_0_to_1)", f"{q_avg:.2f}" if pd.notna(q_avg) else "N/A", delta="SLO >= 0.75", delta_color="normal")
else:
    with col6:
        st.metric("Quality Proxy", "N/A")

# Implement Auto Refresh without external library using st.empty or fragment if available
time.sleep(30)
st.rerun()
