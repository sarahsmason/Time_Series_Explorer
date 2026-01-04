# TimeSeriesExplorer.py
# Date-based interactive time series explorer using Streamlit, Plotly, and Pandas
# Allows users to upload a CSV, select date and value columns,
# choose date ranges and aggregation granularity, and view KPIs and charts.
# Author: Sarah Mason
# Date: 2026-01-03

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Date-based Interactive Visual")

st.title("Interactive Time Series Explorer")

# Upload CSV
# Allow upload or fallback to the default CSV path
DEFAULT_CSV_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "RetailSalesHealthPersonalCare.csv"),
    os.path.join(os.path.expanduser("~"), "Downloads", "RetailSalesHealthPersonalCare.csv"),
    os.path.join(os.getcwd(), "RetailSalesHealthPersonalCare.csv"),
]
DEFAULT_CSV = next((p for p in DEFAULT_CSV_CANDIDATES if p and os.path.exists(p)), None)

uploaded = st.file_uploader("Upload CSV (or leave empty to use default)", type=["csv"])
if uploaded is None:
    if DEFAULT_CSV:
        st.info(f"No upload provided — using default file: {DEFAULT_CSV}")
        df = pd.read_csv(DEFAULT_CSV)
    else:
        st.error("No CSV provided and no default file found. Upload a CSV or place 'RetailSalesHealthPersonalCare.csv' next to this script.")
        # When run directly with `python` the Streamlit runtime may not stop execution; exit explicitly
        raise SystemExit(1)
else:
    df = pd.read_csv(uploaded)

st.sidebar.write("Detected columns:", list(df.columns))

# Helpers to auto-detect columns
def choose_date_column(df):
    candidates = [c for c in df.columns if "date" in c.lower()]
    if candidates:
        return candidates[0]
    for c in df.columns:
        try:
            pd.to_datetime(df[c].dropna().iloc[:5])
            return c
        except Exception:
            continue
    return df.columns[0]

# Let user select date & value columns
date_col = st.sidebar.selectbox("Date column", df.columns, index=list(df.columns).index(choose_date_column(df)))
numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.sidebar.error("No numeric columns detected. Please upload a dataset with a numeric sales/amount column.")
    st.stop()
value_col = st.sidebar.selectbox("Value column", numeric_cols, index=0)

# Parse and sort by date
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col])
df = df.sort_values(date_col)

# Date range selector
min_date = df[date_col].min().date()
max_date = df[date_col].max().date()
start_date, end_date = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Aggregation / Granularity selector (compact)
gran_options = ["Auto (compact)", "Daily", "Weekly", "Monthly", "Quarterly", "Yearly"]
gran_choice = st.sidebar.selectbox("Granularity", gran_options, index=0)
freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Quarterly": "Q", "Yearly": "A"}

# Determine chosen granularity when Auto is selected
if gran_choice.startswith("Auto"):
    span_days = (end_date - start_date).days
    if span_days <= 60:
        chosen = "Daily"
    elif span_days <= 365:
        chosen = "Weekly"
    elif span_days <= 365 * 2:
        chosen = "Monthly"
    elif span_days <= 365 * 5:
        chosen = "Quarterly"
    else:
        chosen = "Yearly"
    st.sidebar.caption(f"Auto selected: {chosen} for {span_days} days")
else:
    chosen = gran_choice

# Filter by date range
mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
filtered = df.loc[mask].copy()
if filtered.empty:
    st.warning("No data in the selected date range. Adjust the range.")
    st.stop()

# Aggregate using resample with chosen frequency
filtered.set_index(date_col, inplace=True)
resampled = filtered[value_col].resample(freq_map[chosen]).sum().reset_index()
resampled = resampled.rename(columns={value_col: "value"})

# Compute KPIs
total_sales = resampled["value"].sum()
avg_per_period = resampled["value"].mean()

# Layout: main chart and right-side KPIs
left_col, right_col = st.columns([3, 1])

with right_col:
    st.markdown("### Highlights")
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
    st.metric(label=f"Avg ({chosen})", value=f"${avg_per_period:,.2f}")

    # Min / Max within the selected date range (based on the resampled series)
    if not resampled.empty:
        min_idx = resampled["value"].idxmin()
        min_row = resampled.loc[min_idx]
        min_val = min_row["value"]
        min_dt = pd.to_datetime(min_row[resampled.columns[0]]).date()
        max_idx = resampled["value"].idxmax()
        max_row = resampled.loc[max_idx]
        max_val = max_row["value"]
        max_dt = pd.to_datetime(max_row[resampled.columns[0]]).date()

        st.metric(label="Min", value=f"${min_val:,.2f}")
        st.caption(f"{min_dt}")
        st.metric(label="Max", value=f"${max_val:,.2f}")
        st.caption(f"{max_dt}")

    st.markdown("---")

with left_col:
    fig = px.line(resampled, x=resampled.columns[0], y="value", title=f"{value_col} — {chosen} sum", markers=True)
    # Format y-axis ticks as currency and set hover template to show dollar values
    fig.update_layout(yaxis_title=value_col)
    fig.update_yaxes(tickformat="$,.2f")
    fig.update_traces(hovertemplate="%{x}<br>%{y:$,.2f}<extra></extra>")
    fig.add_hline(y=avg_per_period, line_dash="dash", line_color="green", annotation_text=f"Avg ({chosen}) = ${avg_per_period:,.2f}", annotation_position="top left")
    st.plotly_chart(fig, use_container_width=True)

# Optionally show table
if st.checkbox("Show filtered table"):
    st.dataframe(filtered.sort_values(date_col))

