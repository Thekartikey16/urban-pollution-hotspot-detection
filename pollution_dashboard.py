import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================
# P_286 URBAN POLLUTION HOTSPOT DASHBOARD
# ==========================================

st.set_page_config(
    page_title="P_286 Pollution Dashboard",
    page_icon="🌍",
    layout="wide"
)


# ==========================================
# LOAD DATA
# ==========================================

DATA_FILE = "dashboard_data.csv"

df = pd.read_csv(DATA_FILE)


# ==========================================
# TITLE
# ==========================================

st.title("🌍 P_286 Urban Pollution Hotspot Detection")
st.markdown(
    "Historical pollution analysis using clustering and geospatial data."
)


# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Filters")

cities = ["All"] + sorted(df["city"].dropna().unique().tolist())

selected_city = st.sidebar.selectbox(
    "Select City",
    cities
)

if selected_city != "All":
    filtered_df = df[df["city"] == selected_city].copy()
else:
    filtered_df = df.copy()


# ==========================================
# METRICS
# ==========================================

total_records = len(filtered_df)

hotspot_records = (
    filtered_df["hotspot_status"] == "HOTSPOT"
).sum()

normal_records = (
    filtered_df["hotspot_status"] == "NORMAL"
).sum()

average_pm25 = filtered_df["pm25"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Hotspot Records",
    f"{hotspot_records:,}"
)

col3.metric(
    "Normal Records",
    f"{normal_records:,}"
)

col4.metric(
    "Average PM2.5",
    f"{average_pm25:.2f}"
)


# ==========================================
# HOTSPOT MAP
# ==========================================

st.subheader("📍 Pollution Hotspot Map")

map_df = filtered_df.dropna(
    subset=["latitude", "longitude"]
).copy()

fig_map = px.scatter_map(
    map_df,
    lat="latitude",
    lon="longitude",
    color="hotspot_status",
    hover_data=[
        "city",
        "pm25",
        "pm10",
        "cluster"
    ],
    zoom=4,
    height=600
)

fig_map.update_layout(
    map_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(
    fig_map,
    use_container_width=True
)


# ==========================================
# POLLUTION PARAMETERS
# ==========================================

st.subheader("📊 Pollution Parameters")

pollution_columns = [
    "pm25",
    "pm10",
    "no2",
    "co",
    "so2",
    "o3"
]

available_columns = [
    column
    for column in pollution_columns
    if column in filtered_df.columns
]

pollution_avg = (
    filtered_df[available_columns]
    .mean()
    .reset_index()
)

pollution_avg.columns = [
    "Pollutant",
    "Average Value"
]

fig_pollution = px.bar(
    pollution_avg,
    x="Pollutant",
    y="Average Value",
    title="Average Pollution Levels"
)

st.plotly_chart(
    fig_pollution,
    use_container_width=True
)


# ==========================================
# CLUSTER ANALYSIS
# ==========================================

st.subheader("🔵 Pollution Cluster Distribution")

cluster_count = (
    filtered_df["cluster"]
    .value_counts()
    .sort_index()
    .reset_index()
)

cluster_count.columns = [
    "Cluster",
    "Records"
]

fig_cluster = px.bar(
    cluster_count,
    x="Cluster",
    y="Records",
    title="Records by Pollution Cluster"
)

st.plotly_chart(
    fig_cluster,
    use_container_width=True
)


# ==========================================
# HOTSPOT TABLE
# ==========================================

st.subheader("🚨 Hotspot Records")

hotspots = filtered_df[
    filtered_df["hotspot_status"] == "HOTSPOT"
]

display_columns = [
    "city",
    "latitude",
    "longitude",
    "pm25",
    "pm10",
    "no2",
    "co",
    "so2",
    "o3",
    "cluster",
    "hotspot_status"
]

display_columns = [
    column
    for column in display_columns
    if column in hotspots.columns
]

st.dataframe(
    hotspots[display_columns].head(100),
    use_container_width=True
)


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "P_286 Urban Pollution Hotspot Detection | "
    "Kaggle Historical Dataset + K-Means Clustering"
)