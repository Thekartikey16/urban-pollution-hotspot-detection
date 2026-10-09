# ==========================================
# P_286 - URBAN POLLUTION HOTSPOT DETECTION
# CLUSTERING AND HOTSPOT DETECTION
# ==========================================

import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from config import (
    POLLUTION_FEATURES,
    N_CLUSTERS,
    RANDOM_STATE
)


# ==========================================
# FILE CONFIGURATION
# ==========================================

INPUT_FILE = r"C:\Users\kartikey singh\Downloads\P286_Kaggle_Dataset\processed_kaggle_pollution.csv"

OUTPUT_FILE = "pollution_clusters.csv"

SCALER_FILE = "pollution_scaler.joblib"

MODEL_FILE = "pollution_kmeans.joblib"


# ==========================================
# LOAD PROCESSED DATA
# ==========================================

print()
print("==========================================")
print("P_286 CLUSTERING")
print("==========================================")

print("Loading:", INPUT_FILE)

df = pd.read_csv(INPUT_FILE)

print()
print("Total records:", len(df))


# ==========================================
# SELECT POLLUTION FEATURES
# ==========================================

X = df[POLLUTION_FEATURES]


# ==========================================
# FEATURE SCALING
# ==========================================

print()
print("Scaling pollution features...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ==========================================
# SAVE SCALER
# ==========================================

joblib.dump(
    scaler,
    SCALER_FILE
)

print(
    "Scaler saved:",
    SCALER_FILE
)


# ==========================================
# CREATE K-MEANS MODEL
# ==========================================

print()
print("Creating K-Means model...")

kmeans = KMeans(
    n_clusters=N_CLUSTERS,
    random_state=RANDOM_STATE,
    n_init=10
)


# ==========================================
# APPLY CLUSTERING
# ==========================================

df["cluster"] = kmeans.fit_predict(
    X_scaled
)


# ==========================================
# SAVE K-MEANS MODEL
# ==========================================

joblib.dump(
    kmeans,
    MODEL_FILE
)

print(
    "K-Means model saved:",
    MODEL_FILE
)


# ==========================================
# CALCULATE CLUSTER POLLUTION SCORE
# ==========================================

cluster_scores = (
    df
    .groupby("cluster")[POLLUTION_FEATURES]
    .mean()
)


# ==========================================
# NORMALIZE CLUSTER SCORES
# ==========================================

cluster_scores_normalized = (
    cluster_scores
    - cluster_scores.min()
) / (
    cluster_scores.max()
    - cluster_scores.min()
)


# ==========================================
# CALCULATE OVERALL POLLUTION SCORE
# ==========================================

cluster_scores_normalized[
    "pollution_score"
] = cluster_scores_normalized.mean(
    axis=1
)


# ==========================================
# IDENTIFY HOTSPOT CLUSTER
# ==========================================

hotspot_cluster = (
    cluster_scores_normalized[
        "pollution_score"
    ]
    .idxmax()
)


# ==========================================
# MARK HOTSPOT RECORDS
# ==========================================

df["hotspot"] = (
    df["cluster"] ==
    hotspot_cluster
)


# ==========================================
# DISPLAY CLUSTER INFORMATION
# ==========================================

print()
print("==========================================")
print("CLUSTER ANALYSIS")
print("==========================================")

print(cluster_scores)


# ==========================================
# DISPLAY HOTSPOT
# ==========================================

print()
print("==========================================")
print("HOTSPOT DETECTION")
print("==========================================")

print(
    "Hotspot Cluster:",
    hotspot_cluster
)

print(
    "Hotspot Records:",
    df["hotspot"].sum()
)


# ==========================================
# SAVE CLUSTERED DATA
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# SAVE HOTSPOT CLUSTER
# ==========================================

with open(
    "hotspot_cluster.txt",
    "w"
) as file:

    file.write(
        str(hotspot_cluster)
    )


# ==========================================
# DISPLAY SAMPLE RESULTS
# ==========================================

print()
print("==========================================")
print("SAMPLE RESULTS")
print("==========================================")

print(
    df[
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
# COMPLETED
# ==========================================

print()
print("==========================================")
print("CLUSTERING COMPLETED")
print("==========================================")

print(
    "Output file:",
    OUTPUT_FILE
)

print(
    "Scaler:",
    SCALER_FILE
)

print(
    "Model:",
    MODEL_FILE
)

print(
    "Hotspot cluster:",
    hotspot_cluster
)

print("==========================================")