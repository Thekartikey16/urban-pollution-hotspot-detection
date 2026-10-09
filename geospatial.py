# ==========================================
# P_286 - URBAN POLLUTION HOTSPOT DETECTION
# GEO-SPATIAL ANALYSIS
# ==========================================


# ==========================================
# IMPORT LIBRARIES
# ==========================================

import pandas as pd
import geopandas as gpd


# ==========================================
# FILE CONFIGURATION
# ==========================================

INPUT_FILE = "pollution_clusters.csv"

OUTPUT_FILE = "pollution_hotspots.geojson"


# ==========================================
# LOAD CLUSTERED DATA
# ==========================================

print()
print("==========================================")
print("P_286 GEO-SPATIAL ANALYSIS")
print("==========================================")

print(
    "Loading:",
    INPUT_FILE
)

df = pd.read_csv(
    INPUT_FILE
)


# ==========================================
# CHECK DATA
# ==========================================

print()
print(
    "Total records:",
    len(df)
)


# ==========================================
# CREATE GEOGRAPHICAL POINTS
# ==========================================

geometry = gpd.points_from_xy(
    df["longitude"],
    df["latitude"]
)


# ==========================================
# CREATE GEODATAFRAME
# ==========================================

gdf = gpd.GeoDataFrame(
    df,
    geometry=geometry,
    crs="EPSG:4326"
)


# ==========================================
# DISPLAY HOTSPOT DATA
# ==========================================

print()
print("==========================================")
print("HOTSPOT LOCATIONS")
print("==========================================")

hotspots = gdf[
    gdf["hotspot"] == True
]

print(
    hotspots[
        [
            "latitude",
            "longitude",
            "pm25",
            "pm10",
            "cluster",
            "hotspot"
        ]
    ].head(10)
)


# ==========================================
# SAVE GEOJSON
# ==========================================

gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)


# ==========================================
# COMPLETED
# ==========================================

print()
print("==========================================")

print(
    "GEO-SPATIAL ANALYSIS COMPLETED"
)

print(
    "GeoJSON file:",
    OUTPUT_FILE
)

print("==========================================")