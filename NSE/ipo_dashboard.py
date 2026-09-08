"""Streamlit dashboard for NSE IPO issue data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
WORKBOOK_PATH = APP_DIR / "nse_ipo_details.xlsx"
SCRIPTS_DIR = APP_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from NSE_IPO_data import NSEIPOData  # noqa: E402


st.set_page_config(
    page_title="NSE IPO Radar",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #17212b; --muted: #65727e; --teal: #087f8c; --orange: #ef8354; --line: #dce5e7; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    [data-testid="stAppViewContainer"] { background: #f4f7f6; }
    [data-testid="stHeader"] { background: transparent; }
    .hero { background: linear-gradient(120deg, #073b4c 0%, #087f8c 62%, #5aa9a7 100%); padding: 2.1rem 2.4rem; border-radius: 18px; color: white; margin-bottom: 1.4rem; }
    .hero h1 { color: white; margin: 0; font-size: 2.35rem; }
    .hero p { color: #d6f2ef; margin: .4rem 0 0; font-size: 1.02rem; }
    .eyebrow { color: #a8e6df; font-size: .76rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .section { border-bottom: 1px solid var(--line); padding: 1.3rem 0 .65rem; margin: .4rem 0 1rem; }
    .section h2 { margin: 0; font-size: 1.35rem; }
    .section p { color: var(--muted); margin: .25rem 0 0; }
    .fact { background: white; border: 1px solid var(--line); border-radius: 12px; padding: 1rem; min-height: 82px; }
    .fact-label { color: var(--muted); font-size: .76rem; text-transform: uppercase; letter-spacing: .07em; }
    .fact-value { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 1.18rem; font-weight: 700; margin-top: .35rem; }
    .note { background: #fff7ed; border-left: 4px solid var(--orange); padding: .8rem 1rem; border-radius: 0 8px 8px 0; color: #6b4632; }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_workbook() -> pd.DataFrame:
    if not WORKBOOK_PATH.exists():
        return pd.DataFrame()
    return pd.read_excel(WORKBOOK_PATH, sheet_name="IPO Details")


def load_data(refresh: bool) -> tuple[pd.DataFrame, str]:
    if refresh:
        try:
            data = NSEIPOData().get_all_ipos()
            if not data.empty:
                data.to_excel(WORKBOOK_PATH, index=False, sheet_name="IPO Details")
                return data, "Live data refreshed from NSE"
        except Exception as error:
            st.warning(f"NSE refresh failed: {error}. Showing the saved workbook instead.")
    return read_workbook(), "Loaded from saved NSE workbook"


def number(value: object) -> float | None:
    try:
        return float(value) if pd.notna(value) else None
    except (TypeError, ValueError):
        return None


def price_high(row: pd.Series) -> float | None:
    value = number(row.get("upper_price"))
    if value is not None:
        return value
    text = str(row.get("issuePrice", ""))
    parts = [number(part) for part in text.replace("Rs.", "").split("to")]
    return next((part for part in reversed(parts) if part is not None), None)


def enrich(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    if "entity_name" not in frame:
        frame["entity_name"] = frame.get("companyName", "Unknown IPO")
    frame["price_high"] = frame.apply(price_high, axis=1)
    if "total_shares" not in frame:
        frame["total_shares"] = frame.get("noOfSharesOffered")
    frame["issue_value_cr"] = frame["total_shares"] * frame["price_high"] / 10_000_000
    frame["bid_shares"] = pd.to_numeric(frame.get("noOfsharesBid"), errors="coerce")
    frame["bid_value_cr"] = frame["bid_shares"] * frame["price_high"] / 10_000_000
    frame["subscription"] = pd.to_numeric(frame.get("noOfTime"), errors="coerce")
    return frame


def fact(label: str, value: str) -> None:
    st.markdown(
        f'<div class="fact"><div class="fact-label">{label}</div><div class="fact-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def display_value(value: object, fallback: str = "Not available") -> str:
    return fallback if value is None or pd.isna(value) or str(value).strip() in ("", "nan") else str(value)


st.sidebar.markdown("## NSE IPO Radar")
refresh = st.sidebar.button("↻  Refresh from NSE", width="stretch")
data, source_message = load_data(refresh)
st.sidebar.caption(source_message)

if data.empty:
    st.error("No IPO data is available. Run NSE_IPO_data.py first or check the NSE connection.")
    st.stop()

data = enrich(data)
segments = sorted(data.get("category", pd.Series(dtype=str)).dropna().astype(str).unique())
selected_segment = st.sidebar.multiselect("Segment", segments, default=segments)
statuses = sorted(data.get("status", pd.Series(dtype=str)).dropna().astype(str).unique())
selected_status = st.sidebar.multiselect("Status", statuses, default=statuses)

filtered = data.copy()
if selected_segment and "category" in filtered:
    filtered = filtered[filtered["category"].astype(str).isin(selected_segment)]
if selected_status and "status" in filtered:
    filtered = filtered[filtered["status"].astype(str).isin(selected_status)]

if filtered.empty:
    st.warning("No IPOs match the selected filters.")
    st.stop()

names = filtered["entity_name"].astype(str).tolist()
selected_name = st.sidebar.selectbox("Select an IPO", names)
selected = filtered[filtered["entity_name"].astype(str) == selected_name].iloc[0]

st.markdown(
    f'<div class="hero"><div class="eyebrow">NSE IPO intelligence · {display_value(selected.get("issue_type"), "issue")}</div>'
    f'<h1>{display_value(selected.get("entity_name"))}</h1>'
    f'<p>{display_value(selected.get("symbol"), "No symbol")} · {display_value(selected.get("category"), "Main issue")} · {display_value(selected.get("status"), "Status unavailable")}</p></div>',
    unsafe_allow_html=True,
)

metric_columns = st.columns(5)
with metric_columns[0]:
    fact("Price band", display_value(selected.get("price_range", selected.get("issuePrice"))))
with metric_columns[1]:
    shares = number(selected.get("total_shares"))
    fact("Total shares", f"{shares:,.0f}" if shares is not None else "Not available")
with metric_columns[2]:
    value = number(selected.get("issue_value_cr"))
    fact("Issue value", f"₹{value:,.2f} Cr" if value is not None else "Not available")
with metric_columns[3]:
    subscription = number(selected.get("subscription"))
    fact("Subscription", f"{subscription:,.2f}×" if subscription is not None else "Not available")
with metric_columns[4]:
    fact("Lot size", display_value(selected.get("lot_size")))

st.markdown('<div class="section"><h2>Issue timeline</h2><p>Key dates reported by NSE for this issue.</p></div>', unsafe_allow_html=True)
timeline = st.columns(3)
for column, label, key in zip(timeline, ("Open date", "Close date", "Listing date"), ("open_date", "close_date", "listing_date")):
    with column:
        fact(label, display_value(selected.get(key, selected.get({"open_date": "issueStartDate", "close_date": "issueEndDate"}.get(key, key)))))

left, right = st.columns([1.08, 1], gap="large")
with left:
    st.markdown('<div class="section"><h2>Issue breakdown</h2><p>Available NSE issue and bid quantities.</p></div>', unsafe_allow_html=True)
    breakdown = pd.DataFrame(
        {"Measure": ["Shares offered", "Shares bid", "Bid value (₹ Cr)", "Subscription"],
         "Value": [shares, number(selected.get("bid_shares")), number(selected.get("bid_value_cr")), subscription]}
    ).set_index("Measure")
    st.bar_chart(breakdown.fillna(0), horizontal=True, color="#087f8c")
with right:
    st.markdown('<div class="section"><h2>IPO comparison</h2><p>Issue value and subscription across filtered issues.</p></div>', unsafe_allow_html=True)
    comparison = filtered[["entity_name", "issue_value_cr", "subscription"]].set_index("entity_name").rename(columns={"issue_value_cr": "Issue value (₹ Cr)", "subscription": "Subscription (×)"})
    st.bar_chart(comparison.fillna(0), color=["#087f8c", "#ef8354"])

st.markdown('<div class="section"><h2>Subscription snapshot</h2><p>Raw NSE subscription fields for the selected issue.</p></div>', unsafe_allow_html=True)
subscription_fields = ["category", "noOfSharesOffered", "noOfsharesBid", "noOfTime", "series", "status"]
available = [field for field in subscription_fields if field in selected.index]
subscription_table = pd.DataFrame({"Field": available, "Value": [selected[field] for field in available]})
subscription_table["Value"] = subscription_table["Value"].map(display_value)
st.dataframe(subscription_table, hide_index=True, width="stretch")

with st.expander("View all IPO records"):
    visible = [column for column in ["entity_name", "symbol", "category", "issuePrice", "issueSize", "issueStartDate", "issueEndDate", "status", "issue_value_cr", "subscription"] if column in filtered]
    st.dataframe(filtered[visible].sort_values("entity_name"), hide_index=True, width="stretch")

with st.expander("View raw NSE fields"):
    raw_table = selected.to_frame("Value")
    raw_table["Value"] = raw_table["Value"].map(display_value)
    st.dataframe(raw_table, width="stretch")

st.markdown('<div class="note">Data source: NSE India public IPO endpoints. Issue value is calculated as shares offered × upper price band and is shown in ₹ crore. Missing NSE fields are left unavailable.</div>', unsafe_allow_html=True)