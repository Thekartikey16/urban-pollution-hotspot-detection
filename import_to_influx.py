import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

URL = "http://localhost:8086"
TOKEN = "kosNqegZv_PvvMcUw1qQHelQ2GS7cCAaMus8YU9D4LB9pEuGzQvySICHWJKZ0VD_1fCl_qBnvDmyjX1vXe-PoA=="
ORG = "P286"
BUCKET = "pollution_data"

df = pd.read_csv("dashboard_data.csv")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

client = InfluxDBClient(
    url=URL,
    token=TOKEN,
    org=ORG,
    timeout=120000
)

write_api = client.write_api(write_options=SYNCHRONOUS)

points = []

for _, row in df.iterrows():

    point = (
        Point("pollution")
        .tag("city", str(row["city"]))
        .tag("state", str(row["state"]))
        .tag("station_id", str(row["station_id"]))
        .tag("cluster", str(row["cluster"]))
        .tag("hotspot_status", str(row["hotspot_status"]))
        .field("pm25", float(row["pm25"]) if pd.notna(row["pm25"]) else 0.0)
        .field("pm10", float(row["pm10"]) if pd.notna(row["pm10"]) else 0.0)
        .field("no2", float(row["no2"]) if pd.notna(row["no2"]) else 0.0)
        .field("co", float(row["co"]) if pd.notna(row["co"]) else 0.0)
        .field("so2", float(row["so2"]) if pd.notna(row["so2"]) else 0.0)
        .field("o3", float(row["o3"]) if pd.notna(row["o3"]) else 0.0)
        .field("aqi", float(row["aqi"]) if pd.notna(row["aqi"]) else 0.0)
        .field("pollution_score", float(row["pollution_score"]))
.field("latitude", float(row["latitude"]))
.field("longitude", float(row["longitude"]))
.time(row["date"])
    )

    points.append(point)

    if len(points) >= 5000:
        write_api.write(
            bucket=BUCKET,
            org=ORG,
            record=points
        )
        print(f"Uploaded {len(points)} records...")
        points = []

if points:
    write_api.write(
        bucket=BUCKET,
        org=ORG,
        record=points
    )
    print(f"Uploaded final {len(points)} records...")

write_api.close()
client.close()

print(f"\nUpload completed: {len(df)} records")