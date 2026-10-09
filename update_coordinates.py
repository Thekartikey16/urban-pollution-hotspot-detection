import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

URL = "http://localhost:8086"
TOKEN = "kosNqegZv_PvvMcUw1qQHelQ2GS7cCAaMus8YU9D4LB9pEuGzQvySICHWJKZ0VD_1fCl_qBnvDmyjX1vXe-PoA=="
ORG = "P286"
BUCKET = "pollution_data"

df = pd.read_csv("dashboard_data.csv")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "latitude", "longitude"])

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
        Point("pollution_coordinates")
        .tag("city", str(row["city"]))
        .tag("state", str(row["state"]))
        .tag("station_id", str(row["station_id"]))
        .tag("hotspot_status", str(row["hotspot_status"]))
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
        print(f"Uploaded {len(points)} coordinate records...")
        points = []

if points:
    write_api.write(
        bucket=BUCKET,
        org=ORG,
        record=points
    )
    print(f"Uploaded final {len(points)} coordinate records...")

write_api.close()
client.close()

print(f"\nCoordinate upload completed: {len(df)} records")