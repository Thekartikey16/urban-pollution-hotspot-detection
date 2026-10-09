# ==========================================
# P_286 - URBAN POLLUTION HOTSPOT DETECTION
# ==========================================


# ==========================================
# HIVEMQ CLOUD CONFIGURATION
# ==========================================

MQTT_BROKER = "a395015caed2401f8487d57a621e13e2.s1.eu.hivemq.cloud"

MQTT_PORT = 8883


# ==========================================
# MQTT LOGIN CREDENTIALS
# ==========================================

MQTT_USERNAME = "kartikey"

MQTT_PASSWORD = "KARTIKEY"


# ==========================================
# MQTT TOPICS
# ==========================================

POLLUTION_TOPIC = "urban_pollution/data"

ALERT_TOPIC = "urban_pollution/alert"


# ==========================================
# DATA FILES
# ==========================================

DATA_FILE = "pollution_data.csv"

LATEST_DATA_FILE = "latest_pollution.json"


# ==========================================
# POLLUTION PARAMETERS
# ==========================================

POLLUTION_FEATURES = [
    "pm25",
    "pm10",
    "no2",
    "co",
    "so2",
    "o3"
]


# ==========================================
# CLUSTERING CONFIGURATION
# ==========================================

N_CLUSTERS = 4

RANDOM_STATE = 42


# ==========================================
# GEO-SPATIAL CONFIGURATION
# ==========================================

LATITUDE_COLUMN = "latitude"

LONGITUDE_COLUMN = "longitude"


# ==========================================
# HOTSPOT CONFIGURATION
# ==========================================

HOTSPOT_CLUSTER = 1

HOTSPOT_THRESHOLD = 0.70
# ==========================================
# ENERGY / ELECTRICITY CONFIGURATION
# ==========================================

TARIFF_PER_KWH = 8.0
