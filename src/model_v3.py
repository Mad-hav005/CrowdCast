import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

import joblib


print("=" * 70)
print("CROWDCAST V3 - CORRECTED MACHINE LEARNING MODEL")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("CrowdCast_ML_Dataset_V2.csv")

print("\nDataset shape:")
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


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

print("\n" + "=" * 70)
print("FEATURE ENGINEERING")
print("=" * 70)


# Listing change rate
df["listing_change_rate"] = (
    df["listing_change"] /
    df["listing_count_prev"].replace(0, np.nan)
)

# Current listings relative to previous listings
df["listing_ratio"] = (
    df["listing_count"] /
    df["listing_count_prev"].replace(0, np.nan)
)

# Listing pressure
df["listing_pressure"] = (
    df["listing_count"] /
    df["section_count"].replace(0, np.nan)
)

# Listings per section
df["listings_per_section"] = (
    df["listing_count"] /
    df["section_count"].replace(0, np.nan)
)

# Available tickets per section
df["available_per_section"] = (
    df["max_available_lot"] /
    df["section_count"].replace(0, np.nan)
)

# Listing / section-group relationship
df["listing_section_ratio"] = (
    df["listing_count"] /
    df["section_group_count"].replace(0, np.nan)
)

# Deal pressure
df["deal_pressure"] = (
    df["deal_rate"] * df["listing_count"]
)


# Event urgency
df["event_urgency"] = pd.cut(
    df["days_until_event"],
    bins=[-np.inf, 3, 7, 14, 30, np.inf],
    labels=[
        "Very_Immediate",
        "Immediate",
        "Near",
        "Medium",
        "Far"
    ]
)


# Event time period
def get_time_period(hour):
    if pd.isna(hour):
        return "Unknown"
    elif hour < 6:
        return "Night"
    elif hour < 12:
        return "Morning"
    elif hour < 18:
        return "Afternoon"
    else:
        return "Evening"


df["event_time_period"] = df["event_hour"].apply(
    get_time_period
)


print("\nNew features created:")
print("- listing_change_rate")
print("- listing_ratio")
print("- listing_pressure")
print("- listings_per_section")
print("- available_per_section")
print("- listing_section_ratio")
print("- deal_pressure")
print("- event_urgency")
print("- event_time_period")


# ============================================================
# 3. REMOVE LEAKAGE / IDENTIFIER COLUMNS
# ============================================================

target = "high_demand_next_snapshot"

remove_columns = [
    target,
    "eventId",
    "eventName",
    "performer_name",
    "venue_name",
    "snapshot_date",
    "event_datetime",
    "listing_change_pct",
    "primary_genre",
    "eventCategory"
]

df = df.drop(
    columns=[
        col for col in remove_columns
        if col in df.columns
    ]
)


# ============================================================
# 4. DEFINE X AND Y
# ============================================================

y = df[target] if target in df.columns else None

# Target was accidentally removed above, so recover it
original = pd.read_csv("CrowdCast_ML_Dataset_V2.csv")
y = original[target]

# Make sure rows match
assert len(df) == len(y)

X = df.drop(
    columns=[target],
    errors="ignore"
)


# ============================================================
# 5. IDENTIFY FEATURES
# ============================================================

numeric_features = X.select_dtypes(
    include=["int64", "float64", "int32", "float32"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()


print("\n" + "=" * 70)
print("FEATURES")
print("=" * 70)

print("\nNumeric features:")
for feature in numeric_features:
    print("-", feature)

print("\nCategorical features:")
for feature in categorical_features:
    print("-", feature)


# ============================================================
# 6. EVENT-LEVEL TRAIN / TEST SPLIT
# ============================================================

print("\n" + "=" * 70)
print("EVENT-LEVEL TRAIN / TEST SPLIT")
print("=" * 70)


# Reload event IDs separately
event_ids = original["eventId"]

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        X,
        y,
        groups=event_ids
    )
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("\nTraining rows:", len(X_train))
print("Testing rows :", len(X_test))

print(
    "Training events:",
    event_ids.iloc[train_idx].nunique()
)

print(
    "Testing events :",
    event_ids.iloc[test_idx].nunique()
)


# ============================================================
# 7. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(
        strategy="most_frequent"
    )),
    ("encoder", OneHotEncoder(
        handle_unknown="ignore"
    ))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])


# ============================================================
# 8. MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=3,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}


# ============================================================
# 9. TRAIN MODELS
# ============================================================

results = []
trained_models = {}

for name, model in models.items():

    print("\n" + "=" * 70)
    print("TRAINING:", name)
    print("=" * 70)

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(X_test)

    probabilities = pipeline.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    print("\nAccuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1 Score :", round(f1, 4))
    print("ROC-AUC  :", round(auc, 4))

    print("\nConfusion Matrix:")
    print(confusion_matrix(
        y_test,
        predictions
    ))

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": auc
    })

    trained_models[name] = pipeline


# ============================================================
# 10. MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "F1",
    ascending=False
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


# ============================================================
# 11. SELECT BEST MODEL
# ============================================================

best_name = results_df.iloc[0]["Model"]

best_model = trained_models[best_name]

print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print("\nBest model based on F1:")
print(best_name)


# ============================================================
# 12. FINAL CLASSIFICATION REPORT
# ============================================================

final_predictions = best_model.predict(X_test)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        final_predictions,
        target_names=[
            "Normal Demand",
            "High Demand"
        ],
        zero_division=0
    )
)


# ============================================================
# 13. SAVE MODEL
# ============================================================

joblib.dump(
    best_model,
    "crowdcast_model_v3.pkl"
)

results_df.to_csv(
    "model_v3_comparison.csv",
    index=False
)


# ============================================================
# 14. FINISH
# ============================================================

print("\n" + "=" * 70)
print("CROWDCAST V3 COMPLETE")
print("=" * 70)

print("\nSaved:")
print("- crowdcast_model_v3.pkl")
print("- model_v3_comparison.csv")