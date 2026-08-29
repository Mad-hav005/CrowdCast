import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


# ============================================================
# CROWDCAST
# Robustness Validation
# ============================================================


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("CrowdCast_ML_Dataset.csv")

TARGET = "high_demand_next_snapshot"

print("=" * 70)
print("CROWDCAST - ROBUSTNESS VALIDATION")
print("=" * 70)

print("\nDataset shape:", df.shape)


# ------------------------------------------------------------
# 2. REMOVE LEAKAGE
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

y = df[TARGET]


# ------------------------------------------------------------
# 3. GROUP BY EVENT
# ------------------------------------------------------------

if "eventId" not in X.columns:
    raise ValueError("eventId column not found.")

groups = X["eventId"]

X = X.drop(
    columns=["eventId"]
)


# ------------------------------------------------------------
# 4. REMOVE HIGH-CARDINALITY / IDENTIFIER COLUMNS
# ------------------------------------------------------------

remove_columns = [
    "record_id",
    "eventName",
    "performer_name",
    "venue_name",
    "event_datetime",
    "snapshot_date",
    "addressCountryCode",
    "primary_genre",
    "eventCategory"
]

X = X.drop(
    columns=remove_columns,
    errors="ignore"
)


# ------------------------------------------------------------
# 5. IDENTIFY FEATURE TYPES
# ------------------------------------------------------------

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()


print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)


# ------------------------------------------------------------
# 6. PREPROCESSING
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
# 7. RANDOM FOREST
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


# ------------------------------------------------------------
# 8. RUN MULTIPLE EVENT-LEVEL SPLITS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RUNNING 5 EVENT-LEVEL VALIDATION SPLITS")
print("=" * 70)


results = []


for split_number in range(1, 6):

    print(
        f"\nRunning validation split {split_number}/5..."
    )

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=100 + split_number
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


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # PREDICTIONS
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        X_test
    )[:, 1]


    # Default threshold
    predictions_default = (
        probabilities >= 0.50
    ).astype(int)


    # CrowdCast optimized threshold
    predictions_optimized = (
        probabilities >= 0.45
    ).astype(int)


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions_optimized
    )

    precision = precision_score(
        y_test,
        predictions_optimized,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions_optimized,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions_optimized,
        zero_division=0
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )


    results.append({

        "Split": split_number,

        "Training Events":
            groups.iloc[train_idx].nunique(),

        "Testing Events":
            groups.iloc[test_idx].nunique(),

        "Accuracy":
            accuracy,

        "Precision":
            precision,

        "Recall":
            recall,

        "F1":
            f1,

        "ROC-AUC":
            auc
    })


    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    print(
        f"ROC-AUC  : {auc:.4f}"
    )


# ------------------------------------------------------------
# 9. RESULTS TABLE
# ------------------------------------------------------------

results_df = pd.DataFrame(results)


print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ------------------------------------------------------------
# 10. MEAN + STANDARD DEVIATION
# ------------------------------------------------------------

metric_columns = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1",
    "ROC-AUC"
]


mean_values = (
    results_df[metric_columns]
    .mean()
)


std_values = (
    results_df[metric_columns]
    .std()
)


print("\n" + "=" * 70)
print("OVERALL VALIDATION PERFORMANCE")
print("=" * 70)


for metric in metric_columns:

    print(
        f"{metric:<10}: "
        f"{mean_values[metric]:.4f} "
        f"+/- "
        f"{std_values[metric]:.4f}"
    )


# ------------------------------------------------------------
# 11. SAVE RESULTS
# ------------------------------------------------------------

results_df.to_csv(
    "robustness_validation.csv",
    index=False
)


summary_df = pd.DataFrame({

    "Metric": metric_columns,

    "Mean": [
        mean_values[m]
        for m in metric_columns
    ],

    "Std": [
        std_values[m]
        for m in metric_columns
    ]

})


summary_df.to_csv(
    "robustness_summary.csv",
    index=False
)


# ------------------------------------------------------------
# 12. FINAL DECISION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CROWDCAST VALIDATION SUMMARY")
print("=" * 70)


mean_f1 = mean_values["F1"]
mean_auc = mean_values["ROC-AUC"]


print(
    f"\nMean F1: {mean_f1:.4f}"
)

print(
    f"Mean ROC-AUC: {mean_auc:.4f}"
)


if mean_f1 >= 0.60 and mean_auc >= 0.80:

    print(
        "\nRESULT: Model performance is reasonably consistent."
    )

    print(
        "The Random Forest can proceed to finalization."
    )

else:

    print(
        "\nRESULT: Model performance needs further investigation."
    )

    print(
        "Do not finalize the model yet."
    )


print("\nSaved:")
print("- robustness_validation.csv")
print("- robustness_summary.csv")

print("\n" + "=" * 70)
print("ROBUSTNESS VALIDATION COMPLETE")
print("=" * 70)