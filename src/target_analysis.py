import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# CROWDCAST
# Target Analysis
#
# Goal:
# Understand the event/snapshot structure and determine
# whether our current demand target is appropriate.
# ============================================================


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("CrowdCast_ML_Dataset.csv")

print("=" * 70)
print("CROWDCAST - TARGET ANALYSIS")
print("=" * 70)

print("\nDataset shape:", df.shape)


# ------------------------------------------------------------
# 2. CONVERT DATES
# ------------------------------------------------------------

df["snapshot_date"] = pd.to_datetime(
    df["snapshot_date"],
    errors="coerce"
)

df["event_datetime"] = pd.to_datetime(
    df["event_datetime"],
    errors="coerce"
)


# ------------------------------------------------------------
# 3. BASIC EVENT STRUCTURE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EVENT STRUCTURE")
print("=" * 70)

print(
    "\nUnique events:",
    df["eventId"].nunique()
)

print(
    "Total snapshots:",
    len(df)
)

snapshots_per_event = (
    df.groupby("eventId")
    .size()
)

print(
    "\nSnapshots per event:"
)

print(
    snapshots_per_event.describe()
)


# ------------------------------------------------------------
# 4. EVENTS WITH MULTIPLE SNAPSHOTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SNAPSHOT COVERAGE")
print("=" * 70)

coverage = (
    snapshots_per_event
    .value_counts()
    .sort_index()
)

print(coverage)


# ------------------------------------------------------------
# 5. CURRENT TARGET
# ------------------------------------------------------------

TARGET = "high_demand_next_snapshot"

print("\n" + "=" * 70)
print("CURRENT TARGET")
print("=" * 70)

print(
    df[TARGET].value_counts()
)

print("\nPercentages:")

print(
    (
        df[TARGET]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)


# ------------------------------------------------------------
# 6. TARGET BY DAYS UNTIL EVENT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGH-DEMAND RATE BY EVENT PROXIMITY")
print("=" * 70)

proximity = (
    df.groupby("days_until_event")[TARGET]
    .agg(
        observations="count",
        high_demand_rate="mean"
    )
)

proximity["high_demand_rate"] *= 100

print(
    proximity
    .sort_index()
    .to_string()
)


# ------------------------------------------------------------
# 7. TARGET BY LISTING COUNT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGH-DEMAND RATE BY LISTING COUNT")
print("=" * 70)

df["listing_count_bin"] = pd.qcut(
    df["listing_count"],
    q=5,
    duplicates="drop"
)

listing_analysis = (
    df.groupby(
        "listing_count_bin",
        observed=True
    )[TARGET]
    .agg(
        observations="count",
        high_demand_rate="mean"
    )
)

listing_analysis["high_demand_rate"] *= 100

print(
    listing_analysis.to_string()
)


# ------------------------------------------------------------
# 8. TARGET BY LISTING CHANGE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGH-DEMAND RATE BY LISTING CHANGE")
print("=" * 70)

df["listing_change_bin"] = pd.qcut(
    df["listing_change"],
    q=5,
    duplicates="drop"
)

change_analysis = (
    df.groupby(
        "listing_change_bin",
        observed=True
    )[TARGET]
    .agg(
        observations="count",
        high_demand_rate="mean"
    )
)

change_analysis["high_demand_rate"] *= 100

print(
    change_analysis.to_string()
)


# ------------------------------------------------------------
# 9. CURRENT TARGET VS LISTING CHANGE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET AND LISTING CHANGE")
print("=" * 70)

print(
    df.groupby(TARGET)["listing_change"]
    .describe()
    .to_string()
)


# ------------------------------------------------------------
# 10. CURRENT TARGET VS DAYS UNTIL EVENT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET AND EVENT PROXIMITY")
print("=" * 70)

print(
    df.groupby(TARGET)["days_until_event"]
    .describe()
    .to_string()
)


# ------------------------------------------------------------
# 11. CHECK CURRENT TARGET LOGIC
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET LOGIC CHECK")
print("=" * 70)

# Reconstruct what the target appears to represent.
#
# We calculate the percentage change in available/listing
# inventory based on the current and previous snapshot.
#
# NOTE:
# This is diagnostic only. We are NOT changing the dataset.

if "listing_count_prev" in df.columns:

    df["calculated_change_rate"] = np.where(
        df["listing_count_prev"] > 0,
        (
            df["listing_count"]
            - df["listing_count_prev"]
        )
        / df["listing_count_prev"],
        np.nan
    )

    print(
        "\nCalculated listing change rate:"
    )

    print(
        df["calculated_change_rate"]
        .describe()
        .to_string()
    )

    print(
        "\nMean change rate by target:"
    )

    print(
        df.groupby(TARGET)["calculated_change_rate"]
        .mean()
    )


# ------------------------------------------------------------
# 12. EVENT-LEVEL TARGET RATE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EVENT-LEVEL TARGET BEHAVIOR")
print("=" * 70)

event_target = (
    df.groupby("eventId")[TARGET]
    .agg(
        snapshots="count",
        high_demand_snapshots="sum",
        high_demand_rate="mean"
    )
)

event_target["high_demand_rate"] *= 100

print(
    "\nEvent-level target statistics:"
)

print(
    event_target[
        [
            "snapshots",
            "high_demand_snapshots",
            "high_demand_rate"
        ]
    ]
    .describe()
    .to_string()
)


# ------------------------------------------------------------
# 13. HOW MANY EVENTS EVER BECOME HIGH DEMAND?
# ------------------------------------------------------------

events_with_high_demand = (
    event_target["high_demand_snapshots"] > 0
).sum()

total_events = len(event_target)

print(
    "\nEvents with at least one high-demand snapshot:",
    events_with_high_demand
)

print(
    "Total events:",
    total_events
)

print(
    "Percentage of events:",
    round(
        events_with_high_demand
        / total_events
        * 100,
        2
    ),
    "%"
)


# ------------------------------------------------------------
# 14. TARGET TRANSITIONS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET TRANSITIONS")
print("=" * 70)

# Sort snapshots within each event.

df_sorted = df.sort_values(
    ["eventId", "snapshot_date"]
).copy()


df_sorted["previous_target"] = (
    df_sorted
    .groupby("eventId")[TARGET]
    .shift(1)
)


transitions = (
    df_sorted[
        df_sorted["previous_target"].notna()
    ]
    .groupby(
        [
            "previous_target",
            TARGET
        ]
    )
    .size()
    .reset_index(
        name="count"
    )
)


print(
    transitions.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 15. CONSECUTIVE HIGH-DEMAND SNAPSHOTS
# ------------------------------------------------------------

high_sequences = (
    df_sorted
    .groupby("eventId")[TARGET]
    .agg(
        total_high=lambda x: int(x.sum()),
        max_consecutive_high=lambda x: (
            x.groupby(
                (x != x.shift()).cumsum()
            )
            .sum()
            .max()
        )
    )
)

print(
    "\nMaximum consecutive high-demand snapshots:"
)

print(
    high_sequences[
        "max_consecutive_high"
    ]
    .describe()
    .to_string()
)


# ------------------------------------------------------------
# 16. VISUALIZATION 1
# HIGH-DEMAND RATE VS DAYS UNTIL EVENT
# ------------------------------------------------------------

plot_data = (
    df.groupby("days_until_event")[TARGET]
    .mean()
    * 100
)

plt.figure(figsize=(10, 6))

plt.plot(
    plot_data.index,
    plot_data.values,
    marker="o"
)

plt.title(
    "High-Demand Rate vs Days Until Event"
)

plt.xlabel(
    "Days Until Event"
)

plt.ylabel(
    "High-Demand Rate (%)"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "target_vs_days.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 17. VISUALIZATION 2
# HIGH-DEMAND RATE VS LISTING COUNT
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    listing_analysis.index.astype(str),
    listing_analysis["high_demand_rate"]
)

plt.title(
    "High-Demand Rate by Listing Count"
)

plt.xlabel(
    "Listing Count Quantile"
)

plt.ylabel(
    "High-Demand Rate (%)"
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "target_vs_listing_count.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 18. VISUALIZATION 3
# TARGET DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(8, 6))

target_counts = (
    df[TARGET]
    .value_counts()
    .sort_index()
)

plt.bar(
    ["Normal Demand", "High Demand"],
    target_counts.values
)

plt.title(
    "CrowdCast Target Distribution"
)

plt.ylabel(
    "Number of Snapshots"
)

plt.tight_layout()

plt.savefig(
    "target_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------------
# 19. SAVE ANALYSIS
# ------------------------------------------------------------

proximity.to_csv(
    "target_by_proximity.csv"
)

listing_analysis.to_csv(
    "target_by_listing_count.csv"
)

change_analysis.to_csv(
    "target_by_listing_change.csv"
)

event_target.to_csv(
    "event_target_analysis.csv"
)


# ------------------------------------------------------------
# 20. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET ANALYSIS COMPLETE")
print("=" * 70)

print(
    "\nThe current target is:",
    TARGET
)

print(
    "\nThe analysis files have been saved."
)

print(
    "\nWe will use these results to determine whether"
)

print(
    "the current target should remain or be redesigned."
)

print("\nGenerated files:")

print("- target_by_proximity.csv")
print("- target_by_listing_count.csv")
print("- target_by_listing_change.csv")
print("- event_target_analysis.csv")
print("- target_vs_days.png")
print("- target_vs_listing_count.png")
print("- target_distribution.png")

print("\n" + "=" * 70)