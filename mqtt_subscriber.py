# ==========================================
# P_286 - MQTT SUBSCRIBER
# Live Pollution + K-Means Hotspot Detection
# ==========================================

import json
import csv
import os
import joblib
import pandas as pd

import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    POLLUTION_TOPIC,
    DATA_FILE,
    LATEST_DATA_FILE
)


# ==========================================
# INFLUXDB CONFIGURATION
# ==========================================

INFLUX_URL = "http://localhost:8086"

# IMPORTANT:
# Keep your existing InfluxDB token here.
INFLUX_TOKEN = "kosNqegZv_PvvMcUw1qQHelQ2GS7cCAaMus8YU9D4LB9pEuGzQvySICHWJKZ0VD_1fCl_qBnvDmyjX1vXe-PoA=="

INFLUX_ORG = "P286"
INFLUX_BUCKET = "pollution_data"


# ==========================================
# LOAD TRAINED CLUSTERING MODEL
# ==========================================

SCALER_FILE = "pollution_scaler.joblib"
MODEL_FILE = "pollution_kmeans.joblib"
HOTSPOT_FILE = "hotspot_cluster.txt"

scaler = joblib.load(SCALER_FILE)
kmeans = joblib.load(MODEL_FILE)

with open(HOTSPOT_FILE, "r") as file:
    hotspot_cluster = int(file.read().strip())

print("==========================================")
print("P_286 LIVE CLUSTERING MODEL LOADED")
print("==========================================")
print(f"Historical Hotspot Cluster: {hotspot_cluster}")
print("==========================================")


# ==========================================
# INFLUXDB CLIENT
# ==========================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)


# ==========================================
# SAVE DATA TO CSV
# ==========================================

def save_to_csv(data):

    file_exists = os.path.exists(DATA_FILE)

    fields = [
        "latitude",
        "longitude",
        "pm25",
        "pm10",
        "no2",
        "co",
        "so2",
        "o3"
    ]

    with open(DATA_FILE, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "pm25": data["pm25"],
            "pm10": data["pm10"],
            "no2": data["no2"],
            "co": data["co"],
            "so2": data["so2"],
            "o3": data["o3"]
        })


# ==========================================
# MQTT CONNECT
# ==========================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to HiveMQ Cloud")

        client.subscribe(POLLUTION_TOPIC)

        print(f"Subscribed to: {POLLUTION_TOPIC}")

    else:

        print(f"MQTT connection failed. Code: {rc}")


# ==========================================
# MQTT MESSAGE
# ==========================================

def on_message(client, userdata, msg):

    try:

        # ----------------------------------
        # Read MQTT data
        # ----------------------------------

        data = json.loads(msg.payload.decode())

        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        pm25 = float(data["pm25"])
        pm10 = float(data["pm10"])
        no2 = float(data["no2"])
        co = float(data["co"])
        so2 = float(data["so2"])
        o3 = float(data["o3"])


        # ----------------------------------
        # Prepare features for K-Means
        # ----------------------------------

        features = pd.DataFrame([{
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "co": co,
            "so2": so2,
            "o3": o3
        }])


        # ----------------------------------
        # Scale data
        # ----------------------------------

        features_scaled = scaler.transform(features)


        # ----------------------------------
        # Predict cluster
        # ----------------------------------

        cluster = int(
            kmeans.predict(features_scaled)[0]
        )


        # ----------------------------------
        # Determine hotspot
        # ----------------------------------

        is_hotspot = (
            cluster == hotspot_cluster
        )

        hotspot_status = (
            "HOTSPOT"
            if is_hotspot
            else "NORMAL"
        )


        # ----------------------------------
        # Display result
        # ----------------------------------

        print()
        print("==========================================")
        print("LIVE POLLUTION DATA")
        print("==========================================")

        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")

        print(f"PM2.5: {pm25}")
        print(f"PM10: {pm10}")
        print(f"NO2: {no2}")
        print(f"CO: {co}")
        print(f"SO2: {so2}")
        print(f"O3: {o3}")

        print("------------------------------------------")

        print(f"Predicted Cluster: {cluster}")
        print(
            f"Historical Hotspot Cluster: "
            f"{hotspot_cluster}"
        )
        print(f"Hotspot: {hotspot_status}")

        print("==========================================")


        # ----------------------------------
        # Save latest JSON
        # ----------------------------------

        data["cluster"] = cluster
        data["hotspot_status"] = hotspot_status

        with open(
            LATEST_DATA_FILE,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


        # ----------------------------------
        # Save CSV
        # ----------------------------------

        save_to_csv(data)


        # ----------------------------------
        # Send to InfluxDB
        # ----------------------------------

        point = (
            Point("pollution")
            .tag("source", "MQTT")
            .tag("cluster", str(cluster))
            .tag("hotspot_status", hotspot_status)

            .field("latitude", latitude)
            .field("longitude", longitude)

            .field("pm25", pm25)
            .field("pm10", pm10)
            .field("no2", no2)
            .field("co", co)
            .field("so2", so2)
            .field("o3", o3)
        )


        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )


        print("Data saved successfully!")
        print("InfluxDB: pollution_data")
        print("Measurement: pollution")
        print(
            f"Cluster: {cluster} | "
            f"Status: {hotspot_status}"
        )


    except Exception as e:

        print()
        print("ERROR PROCESSING MQTT DATA")
        print(e)


# ==========================================
# MQTT CLIENT
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# CONNECT TO HIVEMQ
# ==========================================

print()
print("Connecting to HiveMQ Cloud...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)


# ==========================================
# START MQTT LOOP
# ==========================================

client.loop_forever()# ==========================================
# P_286 - MQTT SUBSCRIBER
# Live Pollution + K-Means Hotspot Detection
# ==========================================

import json
import csv
import os
import joblib
import pandas as pd

import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    POLLUTION_TOPIC,
    DATA_FILE,
    LATEST_DATA_FILE
)


# ==========================================
# INFLUXDB CONFIGURATION
# ==========================================

INFLUX_URL = "http://localhost:8086"

# IMPORTANT:
# Keep your existing InfluxDB token here.
INFLUX_TOKEN = "PASTE_YOUR_EXISTING_INFLUXDB_TOKEN_HERE"

INFLUX_ORG = "P286"
INFLUX_BUCKET = "pollution_data"


# ==========================================
# LOAD TRAINED CLUSTERING MODEL
# ==========================================

SCALER_FILE = "pollution_scaler.joblib"
MODEL_FILE = "pollution_kmeans.joblib"
HOTSPOT_FILE = "hotspot_cluster.txt"

scaler = joblib.load(SCALER_FILE)
kmeans = joblib.load(MODEL_FILE)

with open(HOTSPOT_FILE, "r") as file:
    hotspot_cluster = int(file.read().strip())

print("==========================================")
print("P_286 LIVE CLUSTERING MODEL LOADED")
print("==========================================")
print(f"Historical Hotspot Cluster: {hotspot_cluster}")
print("==========================================")


# ==========================================
# INFLUXDB CLIENT
# ==========================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)


# ==========================================
# SAVE DATA TO CSV
# ==========================================

def save_to_csv(data):

    file_exists = os.path.exists(DATA_FILE)

    fields = [
        "latitude",
        "longitude",
        "pm25",
        "pm10",
        "no2",
        "co",
        "so2",
        "o3"
    ]

    with open(DATA_FILE, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "pm25": data["pm25"],
            "pm10": data["pm10"],
            "no2": data["no2"],
            "co": data["co"],
            "so2": data["so2"],
            "o3": data["o3"]
        })


# ==========================================
# MQTT CONNECT
# ==========================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to HiveMQ Cloud")

        client.subscribe(POLLUTION_TOPIC)

        print(f"Subscribed to: {POLLUTION_TOPIC}")

    else:

        print(f"MQTT connection failed. Code: {rc}")


# ==========================================
# MQTT MESSAGE
# ==========================================

def on_message(client, userdata, msg):

    try:

        # ----------------------------------
        # Read MQTT data
        # ----------------------------------

        data = json.loads(msg.payload.decode())

        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        pm25 = float(data["pm25"])
        pm10 = float(data["pm10"])
        no2 = float(data["no2"])
        co = float(data["co"])
        so2 = float(data["so2"])
        o3 = float(data["o3"])


        # ----------------------------------
        # Prepare features for K-Means
        # ----------------------------------

        features = pd.DataFrame([{
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "co": co,
            "so2": so2,
            "o3": o3
        }])


        # ----------------------------------
        # Scale data
        # ----------------------------------

        features_scaled = scaler.transform(features)


        # ----------------------------------
        # Predict cluster
        # ----------------------------------

        cluster = int(
            kmeans.predict(features_scaled)[0]
        )


        # ----------------------------------
        # Determine hotspot
        # ----------------------------------

        is_hotspot = (
            cluster == hotspot_cluster
        )

        hotspot_status = (
            "HOTSPOT"
            if is_hotspot
            else "NORMAL"
        )


        # ----------------------------------
        # Display result
        # ----------------------------------

        print()
        print("==========================================")
        print("LIVE POLLUTION DATA")
        print("==========================================")

        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")

        print(f"PM2.5: {pm25}")
        print(f"PM10: {pm10}")
        print(f"NO2: {no2}")
        print(f"CO: {co}")
        print(f"SO2: {so2}")
        print(f"O3: {o3}")

        print("------------------------------------------")

        print(f"Predicted Cluster: {cluster}")
        print(
            f"Historical Hotspot Cluster: "
            f"{hotspot_cluster}"
        )
        print(f"Hotspot: {hotspot_status}")

        print("==========================================")


        # ----------------------------------
        # Save latest JSON
        # ----------------------------------

        data["cluster"] = cluster
        data["hotspot_status"] = hotspot_status

        with open(
            LATEST_DATA_FILE,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


        # ----------------------------------
        # Save CSV
        # ----------------------------------

        save_to_csv(data)


        # ----------------------------------
        # Send to InfluxDB
        # ----------------------------------

        point = (
            Point("pollution")
            .tag("source", "MQTT")
            .tag("cluster", str(cluster))
            .tag("hotspot_status", hotspot_status)

            .field("latitude", latitude)
            .field("longitude", longitude)

            .field("pm25", pm25)
            .field("pm10", pm10)
            .field("no2", no2)
            .field("co", co)
            .field("so2", so2)
            .field("o3", o3)
        )


        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )


        print("Data saved successfully!")
        print("InfluxDB: pollution_data")
        print("Measurement: pollution")
        print(
            f"Cluster: {cluster} | "
            f"Status: {hotspot_status}"
        )


    except Exception as e:

        print()
        print("ERROR PROCESSING MQTT DATA")
        print(e)


# ==========================================
# MQTT CLIENT
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# CONNECT TO HIVEMQ
# ==========================================

print()
print("Connecting to HiveMQ Cloud...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)


# ==========================================
# START MQTT LOOP
# ==========================================

client.loop_forever()