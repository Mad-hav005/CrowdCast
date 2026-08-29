import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    GroupShuffleSplit,
    StratifiedGroupKFold,
    cross_val_predict
)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CROWDCAST
# Threshold Optimization
# ============================================================


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("CrowdCast_ML_Dataset.csv")

TARGET = "high_demand_next_snapshot"

print("=" * 70)
print("CROWDCAST - THRESHOLD OPTIMIZATION")
print("=" * 70)

print("\nDataset:", df.shape)


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
# 4. REMOVE IDENTIFIERS
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
# 5. FEATURE TYPES
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
# 6. TRAIN / TEST SPLIT
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

groups_train = groups.iloc[train_idx]
groups_test = groups.iloc[test_idx]


print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

print(
    "Training events:",
    groups_train.nunique()
)

print(
    "Testing events:",
    groups_test.nunique()
)


# ------------------------------------------------------------
# 7. PREPROCESSING
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
# 8. CROWDCAST RANDOM FOREST
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
# 9. OUT-OF-FOLD PROBABILITIES
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("GENERATING OUT-OF-FOLD PREDICTIONS")
print("=" * 70)

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

oof_probabilities = cross_val_predict(
    model,
    X_train,
    y_train,
    groups=groups_train,
    cv=cv,
    method="predict_proba",
    n_jobs=-1
)[:, 1]


print("\nOut-of-fold predictions generated.")


# ------------------------------------------------------------
# 10. FIND BEST THRESHOLD
# ------------------------------------------------------------

thresholds = np.arange(
    0.20,
    0.81,
    0.01
)

threshold_results = []

for threshold in thresholds:

    predictions = (
        oof_probabilities >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_train,
        predictions
    )

    precision = precision_score(
        y_train,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_train,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_train,
        predictions,
        zero_division=0
    )

    threshold_results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    })


threshold_df = pd.DataFrame(
    threshold_results
)


# ------------------------------------------------------------
# 11. BEST F1 THRESHOLD
# ------------------------------------------------------------

best_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

best_threshold = best_row["threshold"]


print("\n" + "=" * 70)
print("BEST THRESHOLD")
print("=" * 70)

print(
    "\nThreshold:",
    round(best_threshold, 2)
)

print(
    "Accuracy:",
    round(best_row["accuracy"], 4)
)

print(
    "Precision:",
    round(best_row["precision"], 4)
)

print(
    "Recall:",
    round(best_row["recall"], 4)
)

print(
    "F1:",
    round(best_row["f1"], 4)
)


# ------------------------------------------------------------
# 12. DISPLAY TOP THRESHOLDS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TOP 10 THRESHOLDS")
print("=" * 70)

print(
    threshold_df
    .sort_values(
        "f1",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 13. TRAIN FINAL MODEL ON TRAINING DATA
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING FINAL MODEL")
print("=" * 70)

model.fit(
    X_train,
    y_train
)


# ------------------------------------------------------------
# 14. TEST PROBABILITIES
# ------------------------------------------------------------

test_probabilities = model.predict_proba(
    X_test
)[:, 1]


# ------------------------------------------------------------
# 15. DEFAULT 0.50 THRESHOLD
# ------------------------------------------------------------

default_predictions = (
    test_probabilities >= 0.50
).astype(int)


# ------------------------------------------------------------
# 16. OPTIMIZED THRESHOLD
# ------------------------------------------------------------

optimized_predictions = (
    test_probabilities >= best_threshold
).astype(int)


# ------------------------------------------------------------
# 17. EVALUATION FUNCTION
# ------------------------------------------------------------

def evaluate_model(
    name,
    predictions
):

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
        test_probabilities
    )

    print("\n" + "-" * 60)
    print(name)
    print("-" * 60)

    print(
        "Accuracy :",
        round(accuracy, 4)
    )

    print(
        "Precision:",
        round(precision, 4)
    )

    print(
        "Recall   :",
        round(recall, 4)
    )

    print(
        "F1 Score :",
        round(f1, 4)
    )

    print(
        "ROC-AUC  :",
        round(auc, 4)
    )

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    return {
        "Model": name,
        "Threshold": 0.50
        if name == "Default Threshold"
        else best_threshold,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": auc
    }


# ------------------------------------------------------------
# 18. COMPARE THRESHOLDS
# ------------------------------------------------------------

default_results = evaluate_model(
    "Default Threshold",
    default_predictions
)

optimized_results = evaluate_model(
    "Optimized Threshold",
    optimized_predictions
)


comparison = pd.DataFrame([
    default_results,
    optimized_results
])


# ------------------------------------------------------------
# 19. SAVE RESULTS
# ------------------------------------------------------------

threshold_df.to_csv(
    "threshold_analysis.csv",
    index=False
)

comparison.to_csv(
    "threshold_comparison.csv",
    index=False
)


# ------------------------------------------------------------
# 20. THRESHOLD PLOT
# ------------------------------------------------------------

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    threshold_df["threshold"],
    threshold_df["precision"],
    label="Precision"
)

plt.plot(
    threshold_df["threshold"],
    threshold_df["recall"],
    label="Recall"
)

plt.plot(
    threshold_df["threshold"],
    threshold_df["f1"],
    label="F1 Score"
)

plt.axvline(
    best_threshold,
    linestyle="--",
    label=f"Best Threshold = {best_threshold:.2f}"
)

plt.title(
    "CrowdCast Classification Threshold Analysis"
)

plt.xlabel(
    "Probability Threshold"
)

plt.ylabel(
    "Score"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "threshold_analysis.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 21. EXAMPLE CROWDCAST PREDICTIONS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXAMPLE CROWDCAST PREDICTIONS")
print("=" * 70)

examples = pd.DataFrame({

    "Actual": y_test.values,

    "Probability": test_probabilities,

    "Risk": np.select(
        [
            test_probabilities < 0.30,
            test_probabilities < 0.60,
            test_probabilities < 0.80
        ],
        [
            "LOW",
            "MODERATE",
            "HIGH"
        ],
        default="CRITICAL"
    )
})

print(
    examples
    .head(15)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 22. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CROWDCAST THRESHOLD ANALYSIS COMPLETE")
print("=" * 70)

print(
    "\nRecommended threshold:",
    round(best_threshold, 2)
)

print("\nGenerated files:")
print("- threshold_analysis.csv")
print("- threshold_comparison.csv")
print("- threshold_analysis.png")