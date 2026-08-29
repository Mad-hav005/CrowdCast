import pandas as pd
import numpy as np

# ============================================================
# CROWDCAST - PREPARE CLEAN ML DATASET
# ============================================================

INPUT_FILE = "CrowdCast_ML_Dataset.csv"
OUTPUT_FILE = "CrowdCast_ML_Dataset_V2.csv"

print("=" * 60)
print("CROWDCAST DATASET PREPARATION")
print("=" * 60)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\nOriginal dataset shape:")
print(df.shape)

# ------------------------------------------------------------
# 2. CLEAN DATES
# ------------------------------------------------------------

df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
df["event_datetime"] = pd.to_datetime(df["event_datetime"])

# Make sure listing count is numeric
df["listing_count"] = pd.to_numeric(
    df["listing_count"], errors="coerce"
)

# ------------------------------------------------------------
# 3. SORT CHRONOLOGICALLY WITHIN EACH EVENT
# ------------------------------------------------------------

df = df.sort_values(
    ["eventId", "snapshot_date"]
).reset_index(drop=True)

# ------------------------------------------------------------
# 4. GET NEXT SNAPSHOT LISTING COUNT
# ------------------------------------------------------------

df["next_listing_count"] = (
    df.groupby("eventId")["listing_count"].shift(-1)
)

# ------------------------------------------------------------
# 5. CALCULATE NEXT-SNAPSHOT CHANGE
# ------------------------------------------------------------

df["next_listing_change_pct"] = np.where(
    df["listing_count"] > 0,
    (
        (df["next_listing_count"] - df["listing_count"])
        / df["listing_count"]
    ) * 100,
    np.nan
)

# ------------------------------------------------------------
# 6. CREATE CLEAN TARGET
#
# 1 = listing count decreases by 25% or more
# 0 = otherwise
# NaN = no next snapshot available
# ------------------------------------------------------------

df["high_demand_next_snapshot"] = np.where(
    df["next_listing_count"].notna(),
    (df["next_listing_change_pct"] <= -25).astype(int),
    np.nan
)

# ------------------------------------------------------------
# 7. REMOVE ROWS WITHOUT A REAL NEXT SNAPSHOT
# ------------------------------------------------------------

before = len(df)

df = df[
    df["high_demand_next_snapshot"].notna()
].copy()

after = len(df)

# Convert target to integer
df["high_demand_next_snapshot"] = (
    df["high_demand_next_snapshot"].astype(int)
)

# ------------------------------------------------------------
# 8. REMOVE TEMPORARY COLUMNS
# ------------------------------------------------------------

df = df.drop(
    columns=[
        "next_listing_count",
        "next_listing_change_pct"
    ]
)

# ------------------------------------------------------------
# 9. SAVE CLEAN DATASET
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ------------------------------------------------------------
# 10. PRINT RESULTS
# ------------------------------------------------------------

print("\nRows removed because no next snapshot existed:")
print(before - after)

print("\nClean dataset shape:")
print(df.shape)

print("\nTarget distribution:")
print(df["high_demand_next_snapshot"].value_counts())

print("\nTarget percentages:")
print(
    df["high_demand_next_snapshot"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nTarget definition:")
print("1 = next snapshot listing count decreased by >= 25%")
print("0 = next snapshot listing count did not decrease by >= 25%")

print("\nOutput file:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("DATASET PREPARATION COMPLETE")
print("=" * 60)