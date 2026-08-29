import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier


# ============================================================
# CROWDCAST
# Feature Importance Analysis
# ============================================================


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("CrowdCast_ML_Dataset.csv")

print("=" * 70)
print("CROWDCAST - FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)

print("\nDataset shape:", df.shape)


# ------------------------------------------------------------
# 2. TARGET
# ------------------------------------------------------------

TARGET = "high_demand_next_snapshot"

y = df[TARGET]


# ------------------------------------------------------------
# 3. REMOVE LEAKAGE
# ------------------------------------------------------------

leakage_columns = [
    TARGET,
    "listing_change_pct"
]

for col in [
    "next_snapshot_listing_count",
    "next_snapshot_available_lot_total",
    "next_snapshot_timestamp",
    "availability_change_pct"
]:
    if col in df.columns:
        leakage_columns.append(col)


X = df.drop(
    columns=leakage_columns,
    errors="ignore"
)


# ------------------------------------------------------------
# 4. GROUP BY EVENT
# ------------------------------------------------------------

if "eventId" not in X.columns:
    raise ValueError("eventId column not found.")

groups = X["eventId"]

X = X.drop(columns=["eventId"])


# ------------------------------------------------------------
# 5. REMOVE HIGH-CARDINALITY / IDENTIFIER COLUMNS
# ------------------------------------------------------------

remove_columns = [
    "record_id",
    "eventName",
    "performer_name",
    "venue_name",
    "event_datetime",
    "snapshot_date",
    "addressCountryCode",
    "primary_genre"
]

X = X.drop(
    columns=remove_columns,
    errors="ignore"
)


# ------------------------------------------------------------
# 6. IDENTIFY FEATURE TYPES
# ------------------------------------------------------------

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()


print("\nNumeric features:")
for feature in numeric_features:
    print("-", feature)

print("\nCategorical features:")
for feature in categorical_features:
    print("-", feature)


# ------------------------------------------------------------
# 7. TRAIN / TEST SPLIT BY EVENT
# ------------------------------------------------------------

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]


# ------------------------------------------------------------
# 8. PREPROCESSING
# ------------------------------------------------------------

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "scaler",
        StandardScaler()
    )
])


categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "encoder",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# ------------------------------------------------------------
# 9. ORIGINAL BEST RANDOM FOREST
# ------------------------------------------------------------

model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
    )
])


print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

model.fit(
    X_train,
    y_train
)

print("\nModel trained successfully.")


# ------------------------------------------------------------
# 10. GET FEATURE NAMES
# ------------------------------------------------------------

feature_names = (
    model
    .named_steps["preprocessor"]
    .get_feature_names_out()
)


# ------------------------------------------------------------
# 11. GET FEATURE IMPORTANCE
# ------------------------------------------------------------

importances = (
    model
    .named_steps["model"]
    .feature_importances_
)


importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
).reset_index(drop=True)


# ------------------------------------------------------------
# 12. CLEAN FEATURE NAMES
# ------------------------------------------------------------

importance_df["feature"] = (
    importance_df["feature"]
    .str.replace(
        "numeric__",
        "",
        regex=False
    )
    .str.replace(
        "categorical__",
        "",
        regex=False
    )
)


print("\n" + "=" * 70)
print("TOP 20 FEATURES")
print("=" * 70)

print(
    importance_df
    .head(20)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 13. SAVE FEATURE IMPORTANCE
# ------------------------------------------------------------

importance_df.to_csv(
    "feature_importance.csv",
    index=False
)

print("\nSaved feature importance:")
print("feature_importance.csv")


# ------------------------------------------------------------
# 14. TOP 15 FEATURE PLOT
# ------------------------------------------------------------

top_features = (
    importance_df
    .head(15)
    .sort_values(
        "importance",
        ascending=True
    )
)


plt.figure(figsize=(12, 8))

plt.barh(
    top_features["feature"],
    top_features["importance"]
)

plt.title(
    "Top 15 Features Influencing CrowdCast Predictions"
)

plt.xlabel(
    "Feature Importance"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.savefig(
    "feature_importance_top15.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 15. GROUP IMPORTANCE BY ORIGINAL FEATURE
# ------------------------------------------------------------

def get_original_feature(feature):

    if "_" in feature:

        # Handle encoded categorical features.
        categorical = categorical_features

        for column in categorical:
            if feature.startswith(column + "_"):
                return column

    return feature


importance_df["original_feature"] = (
    importance_df["feature"]
    .apply(get_original_feature)
)


grouped_importance = (
    importance_df
    .groupby("original_feature")["importance"]
    .sum()
    .sort_values(
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("IMPORTANCE BY ORIGINAL FEATURE")
print("=" * 70)

print(
    grouped_importance
    .to_string(index=False)
)


# ------------------------------------------------------------
# 16. GROUPED IMPORTANCE PLOT
# ------------------------------------------------------------

top_grouped = (
    grouped_importance
    .head(15)
    .sort_values(
        "importance",
        ascending=True
    )
)


plt.figure(figsize=(12, 8))

plt.barh(
    top_grouped["original_feature"],
    top_grouped["importance"]
)

plt.title(
    "CrowdCast Feature Importance by Variable"
)

plt.xlabel(
    "Total Importance"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.savefig(
    "feature_importance_grouped.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 17. FINAL MESSAGE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FEATURE ANALYSIS COMPLETE")
print("=" * 70)

print("\nGenerated files:")
print("- feature_importance.csv")
print("- feature_importance_top15.png")
print("- feature_importance_grouped.png")