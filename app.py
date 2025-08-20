import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Sales Analytics Demo", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("sales_demo_2000.csv", parse_dates=["date"])

df = load_data()

st.title("📊 Sales Analytics Dashboard (Demo)")
st.caption("Dataset: 2,000 orders · Years 2024–2025")

with st.sidebar:
    st.header("Filters")
    min_d, max_d = df["date"].min(), df["date"].max()
    date_rng = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    regions = st.multiselect("Region", sorted(df["region"].unique().tolist()), default=None)
    categories = st.multiselect("Category", sorted(df["category"].unique().tolist()), default=None)
    channels = st.multiselect("Channel", sorted(df["channel"].unique().tolist()), default=None)
    status = st.multiselect("Status", sorted(df["status"].unique().tolist()), default=None)

mask = (df["date"].between(pd.to_datetime(date_rng[0]), pd.to_datetime(date_rng[1])))
if regions: mask &= df["region"].isin(regions)
if categories: mask &= df["category"].isin(categories)
if channels: mask &= df["channel"].isin(channels)
if status: mask &= df["status"].isin(status)
dff = df[mask].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Orders", len(dff))
col2.metric("Revenue", f"{dff['revenue'].sum():,.0f}")
aov = (dff['revenue'].sum()/len(dff)) if len(dff) else 0
col3.metric("AOV", f"{aov:,.0f}")
ret_rate = (len(dff[dff['status']=='Returned'])/len(dff)*100) if len(dff) else 0
col4.metric("Return rate", f"{ret_rate:.2f}%")

st.divider()

rev_month = dff.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
line = alt.Chart(rev_month).mark_line(point=True).encode(
    x=alt.X("month:N", title="Month", sort=None),
    y=alt.Y("revenue:Q", title="Revenue"),
    tooltip=["month","revenue"]
).properties(title="Revenue by Month").interactive()

top_products = dff.groupby("product_name", as_index=False)["revenue"].sum().nlargest(10, "revenue")
bar = alt.Chart(top_products).mark_bar().encode(
    x=alt.X("revenue:Q", title="Revenue"),
    y=alt.Y("product_name:N", sort='-x', title="Product"),
    tooltip=["product_name","revenue"]
).properties(title="Top 10 Products by Revenue")

rev_region = dff.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
bar_region = alt.Chart(rev_region).mark_bar().encode(
    x=alt.X("region:N", title="Region"),
    y=alt.Y("revenue:Q", title="Revenue"),
    tooltip=["region","revenue"]
).properties(title="Revenue by Region")

c1, c2 = st.columns([2,1])
with c1: st.altair_chart(line, use_container_width=True)
with c2: st.altair_chart(bar_region, use_container_width=True)

st.altair_chart(bar, use_container_width=True)

st.caption("Tip: chỉnh bộ lọc ở sidebar để cập nhật biểu đồ theo thời gian thực.")