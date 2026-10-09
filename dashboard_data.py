# ==========================================
# P_286 - URBAN POLLUTION HOTSPOT DETECTION
# DASHBOARD DATA PREPARATION
# ==========================================


# ==========================================
# IMPORT LIBRARIES
# ==========================================

import pandas as pd


# ==========================================
# FILE CONFIGURATION
# ==========================================

INPUT_FILE = "pollution_clusters.csv"

OUTPUT_FILE = "dashboard_data.csv"


# ==========================================
# LOAD CLUSTERED DATA
# ==========================================

print()
print("==========================================")
print("P_286 DASHBOARD DATA")
print("==========================================")

df = pd.read_csv(
    INPUT_FILE
)


# ==========================================
# REMOVE DUPLICATE READINGS
# ==========================================

df = df.drop_duplicates(
    subset=[
        "latitude",
        "longitude",
        "pm25",
        "pm10",
        "no2",
        "co",
        "so2",
        "o3"
    ]
)


# ==========================================
# CREATE HOTSPOT STATUS
# ==========================================

df["hotspot_status"] = df[
    "hotspot"
].apply(
    lambda value:
    "HOTSPOT" if value else "NORMAL"
)


# ==========================================
# CREATE POLLUTION SCORE
# ==========================================

df["pollution_score"] = (
    df["pm25"]
    + df["pm10"]
    + df["no2"]
    + df["so2"]
    + df["o3"]
) / 5


# ==========================================
# SAVE DASHBOARD DATA
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# DISPLAY RESULT
# ==========================================

print()
print(
    "Dashboard records:",
    len(df)
)

print()

print(
    df[
        [
            "latitude",
            "longitude",
            "pm25",
            "pm10",
            "cluster",
            "hotspot_status"
        ]
    ].head(10)
)


# ==========================================
# COMPLETED
# ==========================================

print()
print("==========================================")

print(
    "DASHBOARD DATA CREATED"
)

print(
    "Output:",
    OUTPUT_FILE
)

print("==========================================")