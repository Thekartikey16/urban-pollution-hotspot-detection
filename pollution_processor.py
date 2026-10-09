# ==========================================
# P_286 - URBAN POLLUTION HOTSPOT DETECTION
# DATA PROCESSING
# ==========================================


# ==========================================
# IMPORT LIBRARIES
# ==========================================

import pandas as pd
import numpy as np

from config import POLLUTION_FEATURES


# ==========================================
# FILE CONFIGURATION
# ==========================================

INPUT_FILE = "pollution_data.csv"

OUTPUT_FILE = "processed_pollution_data.csv"


# ==========================================
# LOAD POLLUTION DATA
# ==========================================

print()
print("==========================================")
print("P_286 DATA PROCESSING")
print("==========================================")

print(
    "Loading:",
    INPUT_FILE
)

df = pd.read_csv(
    INPUT_FILE
)


# ==========================================
# DISPLAY DATA INFORMATION
# ==========================================

print()
print("Total records:", len(df))

print()
print("Available columns:")

print(
    df.columns.tolist()
)


# ==========================================
# CHECK MISSING VALUES
# ==========================================

print()
print("==========================================")
print("CHECKING MISSING VALUES")
print("==========================================")

print(
    df.isnull().sum()
)


# ==========================================
# CONVERT POLLUTION FEATURES TO NUMERIC
# ==========================================

for column in POLLUTION_FEATURES:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==========================================
# REMOVE MISSING VALUES
# ==========================================

df = df.dropna(
    subset=POLLUTION_FEATURES
)


# ==========================================
# REMOVE INVALID VALUES
# ==========================================

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.dropna(
    subset=POLLUTION_FEATURES
)


# ==========================================
# DISPLAY CLEAN DATA
# ==========================================

print()
print("==========================================")
print("CLEAN DATA")
print("==========================================")

print(
    "Valid records:",
    len(df)
)


# ==========================================
# POLLUTION STATISTICS
# ==========================================

print()
print("==========================================")
print("POLLUTION STATISTICS")
print("==========================================")

print(
    df[POLLUTION_FEATURES].describe()
)


# ==========================================
# SAVE PROCESSED DATA
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# PROCESS COMPLETED
# ==========================================

print()
print("==========================================")

print(
    "DATA PROCESSING COMPLETED"
)

print(
    "Processed file:",
    OUTPUT_FILE
)

print("==========================================")