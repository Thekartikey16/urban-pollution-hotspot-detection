import paho.mqtt.client as mqtt
import json
import time

# HiveMQ Cloud details
broker = "a395015caed2401f8487d57a621e13e2.s1.eu.hivemq.cloud"
port = 8883

username = "kartikey"
password = "KARTIKEY"

topic = "sensor/temp"

payload = {
    "device_id": "ESP32_001",
    "temperature": 25.4,
    "humidity": 60
}

# Create MQTT client
client = mqtt.Client()

# Authentication
client.username_pw_set(username, password)

# Enable TLS
client.tls_set()

# Connect to HiveMQ Cloud
client.connect(broker, port, 60)

# Measure publishing time
start = time.time()

result = client.publish(
    topic,
    json.dumps(payload)
)

result.wait_for_publish()

end = time.time()

print("Published")
print("Time :", round((end - start) * 1000, 2), "ms")

client.disconnect()