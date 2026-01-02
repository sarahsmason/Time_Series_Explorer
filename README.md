# TimeSeriesExplorer.py

A Streamlit app that loads a time-series CSV and displays an interactive, date-aggregated chart with simple KPIs.

## Features 
- Upload a CSV or use the default CSV file path.
- Auto-detects a date column and a numeric value column.
- Selectable date range and automatic or manual aggregation (Daily / Weekly / Monthly / Quarterly / Yearly).
- KPIs on the right: Total Sales and Average (formatted as currency).
- Min / Max values (currency formatted) with their dates shown as captions.
- Plotly chart with currency-formatted y-axis and dollar-valued hover tooltips.
- Optional table display of the filtered (date-range) data.

## Requirements 
- Python 3.11 (tested in a conda environment)
- Packages: streamlit, pandas, plotly

Install with pip (recommended in your environment):

```bash
pip install streamlit pandas plotly
```

## Running the app 
From the script directory run:

```bash
streamlit run dashboardsample.py
```

Then open http://localhost:8501 in your browser. If Streamlit prompts for an onboarding email on first run, press Enter to skip.

## Configuration & Notes 
- Default CSV path is set at the top of the file:

```python
DEFAULT_CSV = "RetailSalesHealthPersonalCare.csv"
```

Source for csv is : U.S. Census Bureau, Retail Sales: Health and Personal Care Stores [MRTSMPCSM446USN], retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/MRTSMPCSM446USN, December 25, 2025.

To use the CSV shipped in this workspace, either upload it in the UI or change that line to a relative path such as:

```python
DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "RetailSalesHealthPersonalCare.csv")
```

- The script auto-detects the date and numeric columns but allows manual selection from the sidebar.
- Aggregation uses pandas `resample()` on the date index — the app resamples the selected numeric column using the selected granularity.

## Quick troubleshooting 
- "Nothing shows / app doesn't start": check the terminal where you ran `streamlit run` for errors. On first-run, Streamlit may prompt for an email — press Enter to continue.
- Missing packages: install `streamlit`, `pandas`, and `plotly` in the environment you use to run the app.
- If you see no data in the selected date range, widen the date range in the sidebar.

## Development / Editing 
- Syntax check: `python -m py_compile dashboardsample.py`
- To change date formatting under Min/Max captions or metric displays, edit the `min_dt`/`max_dt` formatting and any `st.metric` displays.
- Chart formatting is handled via Plotly `update_yaxes(tickformat="$,.2f")` and `update_traces(hovertemplate=...)` in the file.

## License
This is a utility script for time series analysis. Feel free to adapt.

