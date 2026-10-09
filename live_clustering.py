# ==========================================
# P_286 - LIVE POLLUTION CLUSTERING
# ==========================================

import json
import joblib
import numpy as np

from config import POLLUTION_FEATURES


# ==========================================
# FILES
# ==========================================

DATA_FILE = "latest_pollution.json"

SCALER_FILE = "pollution_scaler.joblib"

MODEL_FILE = "pollution_kmeans.joblib"

HOTSPOT_FILE = "hotspot_cluster.txt"


# ==========================================
# LOAD MODEL
# ==========================================

scaler = joblib.load(
    SCALER_FILE
)

kmeans = joblib.load(
    MODEL_FILE
)


# ==========================================
# LOAD HOTSPOT CLUSTER
# ==========================================

with open(
    HOTSPOT_FILE,
    "r"
) as file:

    hotspot_cluster = int(
        file.read().strip()
    )


# ==========================================
# LOAD LIVE DATA
# ==========================================

with open(
    DATA_FILE,
    "r"
) as file:

    data = json.load(file)


# ==========================================
# CREATE FEATURE ARRAY
# ==========================================

import pandas as pd

features = pd.DataFrame([{
    "pm25": float(data["pm25"]),
    "pm10": float(data["pm10"]),
    "no2": float(data["no2"]),
    "co": float(data["co"]),
    "so2": float(data["so2"]),
    "o3": float(data["o3"])
}])


# ==========================================
# SCALE LIVE DATA
# ==========================================

features_scaled = scaler.transform(
    features
)


# ==========================================
# PREDICT CLUSTER
# ==========================================

cluster = int(
    kmeans.predict(
        features_scaled
    )[0]
)


# ==========================================
# HOTSPOT DETECTION
# ==========================================

is_hotspot = (
    cluster == hotspot_cluster
)


# ==========================================
# DISPLAY RESULT
# ==========================================

print()
print("==========================================")
print("P_286 LIVE CLUSTERING")
print("==========================================")

print(
    "Latitude:",
    data["latitude"]
)

print(
    "Longitude:",
    data["longitude"]
)

print(
    "PM2.5:",
    data["pm25"]
)

print(
    "PM10:",
    data["pm10"]
)

print(
    "NO2:",
    data["no2"]
)

print(
    "CO:",
    data["co"]
)

print(
    "SO2:",
    data["so2"]
)

print(
    "O3:",
    data["o3"]
)

print()
print(
    "Predicted Cluster:",
    cluster
)

print(
    "Historical Hotspot Cluster:",
    hotspot_cluster
)

print(
    "Hotspot:",
    "YES" if is_hotspot else "NO"
)

print("==========================================")