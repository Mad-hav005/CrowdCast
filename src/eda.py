import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CROWDCAST - EVENT OVERCROWDING PREDICTOR
# Phase 1: Exploratory Data Analysis
# ==========================================

# Load dataset
df = pd.read_csv("CrowdCast_Festival_Clean.csv")

# ------------------------------------------
# 1. BASIC DATASET INFORMATION
# ------------------------------------------

print("\n" + "=" * 60)
print("CROWDCAST DATASET")
print("=" * 60)

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())

print("\nDataset Information:")
print(df.info())

# ------------------------------------------
# 2. MISSING VALUES
# ------------------------------------------

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing = df.isnull().sum()

print(missing)

# ------------------------------------------
# 3. DUPLICATES
# ------------------------------------------

print("\n" + "=" * 60)
print("DUPLICATES")
print("=" * 60)

print("Duplicate rows:", df.duplicated().sum())

# ------------------------------------------
# 4. ATTENDANCE STATISTICS
# ------------------------------------------

print("\n" + "=" * 60)
print("ATTENDANCE STATISTICS")
print("=" * 60)

print(df["attendance"].describe())

print("\nUnique attendance values:")
print(df["attendance"].nunique())

# ------------------------------------------
# 5. GENRE ANALYSIS
# ------------------------------------------

print("\n" + "=" * 60)
print("MUSIC GENRE ANALYSIS")
print("=" * 60)

print("\nNumber of unique genres:")
print(df["music_genre"].nunique())

print("\nMost common genres:")
print(df["genre_primary"].value_counts().head(15))

# ------------------------------------------
# 6. LOCATION ANALYSIS
# ------------------------------------------

print("\n" + "=" * 60)
print("LOCATION ANALYSIS")
print("=" * 60)

print("\nNumber of unique locations:")
print(df["location"].nunique())

print("\nTop locations:")
print(df["location"].value_counts().head(15))

# ------------------------------------------
# 7. AVERAGE ATTENDANCE BY GENRE
# ------------------------------------------

genre_attendance = (
    df.groupby("genre_primary")["attendance"]
    .agg(["count", "mean", "median", "min", "max"])
    .sort_values("mean", ascending=False)
)

print("\n" + "=" * 60)
print("ATTENDANCE BY GENRE")
print("=" * 60)

print(genre_attendance.head(20))

# ------------------------------------------
# 8. AVERAGE ATTENDANCE BY LOCATION
# ------------------------------------------

location_attendance = (
    df.groupby("location")["attendance"]
    .agg(["count", "mean", "median", "min", "max"])
    .sort_values("mean", ascending=False)
)

print("\n" + "=" * 60)
print("ATTENDANCE BY LOCATION")
print("=" * 60)

print(location_attendance.head(20))

# ------------------------------------------
# 9. ATTENDANCE DISTRIBUTION
# ------------------------------------------

plt.figure(figsize=(10, 6))

sns.histplot(
    df["attendance"],
    bins=20,
    kde=True
)

plt.title("Distribution of Festival Attendance")
plt.xlabel("Attendance")
plt.ylabel("Number of Festivals")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 10. TOP GENRES BY AVERAGE ATTENDANCE
# ------------------------------------------

top_genres = (
    df.groupby("genre_primary")["attendance"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(12, 6))

sns.barplot(
    x=top_genres.values,
    y=top_genres.index
)

plt.title("Top 10 Genres by Average Attendance")
plt.xlabel("Average Attendance")
plt.ylabel("Genre")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 11. ATTENDANCE BY GENRE - BOXPLOT
# ------------------------------------------

top_genre_names = (
    df["genre_primary"]
    .value_counts()
    .head(10)
    .index
)

genre_filtered = df[
    df["genre_primary"].isin(top_genre_names)
]

plt.figure(figsize=(14, 7))

sns.boxplot(
    data=genre_filtered,
    x="genre_primary",
    y="attendance"
)

plt.title("Attendance Distribution Across Major Genres")
plt.xlabel("Genre")
plt.ylabel("Attendance")

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# ------------------------------------------
# 12. ATTENDANCE BY AGE GROUP
# ------------------------------------------

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="age_min",
    y="attendance",
    size="age_max",
    sizes=(40, 200),
    alpha=0.7
)

plt.title("Attendance vs Minimum Visitor Age")
plt.xlabel("Minimum Visitor Age")
plt.ylabel("Attendance")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 13. ATTENDANCE BY LOCATION
# ------------------------------------------

top_locations = (
    df["location"]
    .value_counts()
    .head(10)
    .index
)

location_filtered = df[
    df["location"].isin(top_locations)
]

plt.figure(figsize=(14, 7))

sns.boxplot(
    data=location_filtered,
    x="location",
    y="attendance"
)

plt.title("Attendance Distribution by Major Locations")
plt.xlabel("Location")
plt.ylabel("Attendance")

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# ------------------------------------------
# 14. LOG ATTENDANCE DISTRIBUTION
# ------------------------------------------

df["log_attendance"] = np.log1p(df["attendance"])

plt.figure(figsize=(10, 6))

sns.histplot(
    df["log_attendance"],
    bins=20,
    kde=True
)

plt.title("Log-Transformed Attendance Distribution")
plt.xlabel("Log(Attendance + 1)")
plt.ylabel("Number of Festivals")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 15. FINAL SUMMARY
# ------------------------------------------

print("\n" + "=" * 60)
print("EDA COMPLETE")
print("=" * 60)

print("\nDataset size:", df.shape)

print("Unique genres:", df["genre_primary"].nunique())

print("Unique locations:", df["location"].nunique())

print(
    "Attendance range:",
    df["attendance"].min(),
    "-",
    df["attendance"].max()
)

print(
    "\nMean attendance:",
    round(df["attendance"].mean(), 2)
)

print(
    "Median attendance:",
    round(df["attendance"].median(), 2)
)

print("\nEDA completed successfully.")