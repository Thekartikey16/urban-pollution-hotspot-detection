# ==========================================
# P_286 - PREPARE DATA FOR VERCEL DEPLOYMENT
# Creates optimized JSON files from the CSV
# ==========================================

import pandas as pd
import json
import os


# ==========================================
# CONFIGURATION
# ==========================================

INPUT_FILE = "dashboard_data.csv"

OUTPUT_DIR = "public/data"


# ==========================================
# LOAD DATA
# ==========================================

print()
print("==========================================")
print("P_286 DEPLOY DATA PREPARATION")
print("==========================================")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} records")


# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# 1. SUMMARY STATISTICS
# ==========================================

cities_list = sorted(
    df["city"].dropna().unique().tolist()
)

summary = {
    "total_records": int(len(df)),
    "hotspot_records": int(
        (df["hotspot_status"] == "HOTSPOT").sum()
    ),
    "normal_records": int(
        (df["hotspot_status"] == "NORMAL").sum()
    ),
    "average_pm25": round(
        float(df["pm25"].mean()), 2
    ),
    "average_pm10": round(
        float(df["pm10"].mean()), 2
    ),
    "average_no2": round(
        float(df["no2"].mean()), 2
    ),
    "average_co": round(
        float(df["co"].mean()), 2
    ),
    "average_so2": round(
        float(df["so2"].mean()), 2
    ),
    "average_o3": round(
        float(df["o3"].mean()), 2
    ),
    "cities": cities_list,
    "total_cities": len(cities_list),
    "clusters": {
        str(k): int(v)
        for k, v in df["cluster"]
        .value_counts()
        .sort_index()
        .items()
    }
}

with open(
    f"{OUTPUT_DIR}/summary.json", "w"
) as f:
    json.dump(summary, f)

print("Created: summary.json")


# ==========================================
# 2. CITY-LEVEL STATISTICS
# ==========================================

city_stats = []

for city in cities_list:

    city_df = df[df["city"] == city]

    city_stats.append({
        "city": city,
        "total_records": int(len(city_df)),
        "hotspot_records": int(
            (city_df["hotspot_status"] == "HOTSPOT").sum()
        ),
        "normal_records": int(
            (city_df["hotspot_status"] == "NORMAL").sum()
        ),
        "avg_pm25": round(
            float(city_df["pm25"].mean()), 2
        ),
        "avg_pm10": round(
            float(city_df["pm10"].mean()), 2
        ),
        "avg_no2": round(
            float(city_df["no2"].mean()), 2
        ),
        "avg_co": round(
            float(city_df["co"].mean()), 2
        ),
        "avg_so2": round(
            float(city_df["so2"].mean()), 2
        ),
        "avg_o3": round(
            float(city_df["o3"].mean()), 2
        ),
        "avg_lat": round(
            float(city_df["latitude"].mean()), 6
        ),
        "avg_lon": round(
            float(city_df["longitude"].mean()), 6
        ),
        "clusters": {
            str(k): int(v)
            for k, v in city_df["cluster"]
            .value_counts()
            .sort_index()
            .items()
        }
    })

with open(
    f"{OUTPUT_DIR}/city_stats.json", "w"
) as f:
    json.dump(city_stats, f)

print("Created: city_stats.json")


# ==========================================
# 3. MAP POINTS (SAMPLED FOR PERFORMANCE)
# ==========================================

# Sample up to 5000 points for the map
map_df = df.dropna(
    subset=["latitude", "longitude"]
).copy()

if len(map_df) > 5000:

    # Keep all hotspot points
    hotspot_df = map_df[
        map_df["hotspot_status"] == "HOTSPOT"
    ]

    normal_df = map_df[
        map_df["hotspot_status"] == "NORMAL"
    ]

    # Sample from normal
    sample_size = min(
        5000 - len(hotspot_df),
        len(normal_df)
    )

    normal_sample = normal_df.sample(
        n=sample_size,
        random_state=42
    )

    map_df = pd.concat(
        [hotspot_df, normal_sample],
        ignore_index=True
    )

map_points = []

for _, row in map_df.iterrows():

    map_points.append({
        "lat": round(float(row["latitude"]), 4),
        "lon": round(float(row["longitude"]), 4),
        "city": str(row["city"]),
        "pm25": round(float(row["pm25"]), 1),
        "pm10": round(float(row["pm10"]), 1),
        "no2": round(float(row["no2"]), 1),
        "co": round(float(row["co"]), 2),
        "so2": round(float(row["so2"]), 1),
        "o3": round(float(row["o3"]), 1),
        "cluster": int(row["cluster"]),
        "status": str(row["hotspot_status"])
    })

with open(
    f"{OUTPUT_DIR}/map_points.json", "w"
) as f:
    json.dump(map_points, f)

print(f"Created: map_points.json ({len(map_points)} points)")


# ==========================================
# 4. HOTSPOT TABLE (TOP 200)
# ==========================================

hotspot_df = df[
    df["hotspot_status"] == "HOTSPOT"
].head(200)

hotspot_table = []

for _, row in hotspot_df.iterrows():

    hotspot_table.append({
        "city": str(row["city"]),
        "lat": round(float(row["latitude"]), 4),
        "lon": round(float(row["longitude"]), 4),
        "pm25": round(float(row["pm25"]), 1),
        "pm10": round(float(row["pm10"]), 1),
        "no2": round(float(row["no2"]), 1),
        "co": round(float(row["co"]), 2),
        "so2": round(float(row["so2"]), 1),
        "o3": round(float(row["o3"]), 1),
        "cluster": int(row["cluster"]),
        "status": str(row["hotspot_status"]),
        "score": round(
            float(row["pollution_score"]), 1
        )
    })

with open(
    f"{OUTPUT_DIR}/hotspot_table.json", "w"
) as f:
    json.dump(hotspot_table, f)

print(f"Created: hotspot_table.json ({len(hotspot_table)} records)")


# ==========================================
# 5. POLLUTION AVERAGES BY CITY
# ==========================================

pollutants = ["pm25", "pm10", "no2", "co", "so2", "o3"]

city_pollution = []

for city in cities_list:

    city_df = df[df["city"] == city]

    entry = {"city": city}

    for p in pollutants:
        entry[p] = round(
            float(city_df[p].mean()), 2
        )

    city_pollution.append(entry)

with open(
    f"{OUTPUT_DIR}/city_pollution.json", "w"
) as f:
    json.dump(city_pollution, f)

print("Created: city_pollution.json")


# ==========================================
# COMPLETED
# ==========================================

print()
print("==========================================")
print("DEPLOY DATA PREPARATION COMPLETED")
print("==========================================")

# Show total file sizes
total_size = 0

for filename in os.listdir(OUTPUT_DIR):

    filepath = os.path.join(
        OUTPUT_DIR, filename
    )

    size = os.path.getsize(filepath)

    total_size += size

    print(
        f"  {filename}: "
        f"{size / 1024:.1f} KB"
    )

print(f"\n  Total: {total_size / 1024:.1f} KB")
print("==========================================")
