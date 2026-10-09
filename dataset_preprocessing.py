import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# P_286 - Kaggle Dataset Preprocessing
# ---------------------------------------------------------

# Kaggle dataset location
DATASET_DIR = Path.home() / "Downloads" / "P286_Kaggle_Dataset"

STATION_DATA = DATASET_DIR / "station_day.csv"
STATIONS = DATASET_DIR / "stations.csv"
CITY_COORDINATES = DATASET_DIR / "city_coordinates.csv"

# Output file
OUTPUT_FILE = DATASET_DIR / "processed_kaggle_pollution.csv"


print("Loading dataset...")

# Load daily station pollution data
pollution = pd.read_csv(STATION_DATA, low_memory=False)

# Load station information
stations = pd.read_csv(STATIONS)

# Load city coordinates
coordinates = pd.read_csv(CITY_COORDINATES)


print("Pollution records:", len(pollution))
print("Stations:", pollution["StationId"].nunique())
print("Cities:", coordinates["City"].nunique())


# ---------------------------------------------------------
# 1. Add station information
# ---------------------------------------------------------

pollution = pollution.merge(
    stations[["StationId", "StationName", "City", "State"]],
    on="StationId",
    how="left"
)


# ---------------------------------------------------------
# 2. Add latitude and longitude
# ---------------------------------------------------------

pollution = pollution.merge(
    coordinates[["City", "State", "Latitude", "Longitude"]],
    on=["City", "State"],
    how="left"
)


# ---------------------------------------------------------
# 3. Rename columns to P_286 format
# ---------------------------------------------------------

pollution = pollution.rename(columns={
    "Date": "date",
    "StationId": "station_id",
    "StationName": "station_name",
    "City": "city",
    "State": "state",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "PM2.5": "pm25",
    "PM10": "pm10",
    "NO2": "no2",
    "CO": "co",
    "SO2": "so2",
    "O3": "o3",
    "AQI": "aqi"
})

# ---------------------------------------------------------
# 4. Convert date
# ---------------------------------------------------------

pollution["date"] = pd.to_datetime(
    pollution["date"],
    errors="coerce"
)


# ---------------------------------------------------------
# 5. Select required columns
# ---------------------------------------------------------

required_columns = [
    "date",
    "station_id",
    "station_name",
    "city",
    "state",
    "latitude",
    "longitude",
    "pm25",
    "pm10",
    "no2",
    "co",
    "so2",
    "o3",
    "aqi"
]

pollution = pollution[required_columns]


# ---------------------------------------------------------
# 6. Handle missing pollution values
# ---------------------------------------------------------

pollution_features = [
    "pm25",
    "pm10",
    "no2",
    "co",
    "so2",
    "o3"
]

for column in pollution_features:
    pollution[column] = pd.to_numeric(
        pollution[column],
        errors="coerce"
    )

    # First: fill using the station median
    pollution[column] = pollution.groupby(
        "station_id"
    )[column].transform(
        lambda x: x.fillna(x.median())
    )

    # Second: fill any remaining missing values
    # using the overall dataset median
    pollution[column] = pollution[column].fillna(
        pollution[column].median()
    )

# ---------------------------------------------------------
# 7. Remove records without coordinates
# ---------------------------------------------------------

before = len(pollution)

pollution = pollution.dropna(
    subset=["latitude", "longitude"]
)

after = len(pollution)

print("Records removed because of missing coordinates:", before - after)


# ---------------------------------------------------------
# 8. Remove rows where pollution values are unavailable
# ---------------------------------------------------------

pollution = pollution.dropna(
    subset=pollution_features,
    how="all"
)


# ---------------------------------------------------------
# 9. Save processed dataset
# ---------------------------------------------------------

pollution.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n======================================")
print("P_286 PREPROCESSING COMPLETE")
print("======================================")
print("Output:", OUTPUT_FILE)
print("Records:", len(pollution))
print("Stations:", pollution["station_id"].nunique())
print("Cities:", pollution["city"].nunique())
print("\nColumns:")
print(list(pollution.columns))