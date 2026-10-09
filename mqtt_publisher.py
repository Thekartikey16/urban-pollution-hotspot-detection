# ==========================================
# P_286 - MQTT POLLUTION DATA PUBLISHER
# ==========================================


# ==========================================
# IMPORT LIBRARIES
# ==========================================

import json
import random
import time

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    POLLUTION_TOPIC
)


# ==========================================
# MQTT CLIENT CONFIGURATION
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set()


# ==========================================
# CONNECT TO HIVEMQ CLOUD
# ==========================================

print("Connecting to HiveMQ Cloud...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

print("Connected successfully!")


# ==========================================
# PUBLISH POLLUTION DATA
# ==========================================

while True:

    pollution_data = {

        "latitude": round(
            random.uniform(28.60, 28.75), 6
        ),

        "longitude": round(
            random.uniform(77.35, 77.55), 6
        ),

        "pm25": round(
            random.uniform(20, 180), 2
        ),

        "pm10": round(
            random.uniform(30, 250), 2
        ),

        "no2": round(
            random.uniform(10, 100), 2
        ),

        "co": round(
            random.uniform(0.2, 5.0), 2
        ),

        "so2": round(
            random.uniform(5, 80), 2
        ),

        "o3": round(
            random.uniform(10, 120), 2
        )
    }


# ==========================================
# CONVERT DATA TO JSON
# ==========================================

    payload = json.dumps(
        pollution_data
    )


# ==========================================
# PUBLISH TO MQTT TOPIC
# ==========================================

    result = client.publish(
        POLLUTION_TOPIC,
        payload
    )


# ==========================================
# DISPLAY PUBLISHED DATA
# ==========================================

    print(
        "Published:",
        payload
    )


# ==========================================
# WAIT BEFORE NEXT READING
# ==========================================

    time.sleep(5)