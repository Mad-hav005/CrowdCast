import pandas as pd
import numpy as np

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

def engineer_features(raw_data: dict) -> pd.DataFrame:
    """
    Takes a raw data dictionary (matching PredictionRequest fields) and
    calculates derived features exactly as in the training script.
    Returns a pandas DataFrame with columns ordered exactly as expected
    by the preprocessor in the scikit-learn pipeline.
    """
    # 1. Create a pandas DataFrame from raw inputs
    df = pd.DataFrame([raw_data])
    
    # 2. Calculate derived features exactly as in training
    df["listing_change_rate"] = (
        df["listing_change"] /
        df["listing_count_prev"].replace(0, np.nan)
    )

    df["listing_ratio"] = (
        df["listing_count"] /
        df["listing_count_prev"].replace(0, np.nan)
    )

    df["listing_pressure"] = (
        df["listing_count"] /
        df["section_count"].replace(0, np.nan)
    )

    df["listings_per_section"] = (
        df["listing_count"] /
        df["section_count"].replace(0, np.nan)
    )

    df["available_per_section"] = (
        df["max_available_lot"] /
        df["section_count"].replace(0, np.nan)
    )

    df["listing_section_ratio"] = (
        df["listing_count"] /
        df["section_group_count"].replace(0, np.nan)
    )

    df["deal_pressure"] = (
        df["deal_rate"] * df["listing_count"]
    )

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
    # Convert category type to object/string so it behavior matches training data dtype
    df["event_urgency"] = df["event_urgency"].astype(object)

    df["event_time_period"] = df["event_hour"].apply(
        get_time_period
    )
    
    # 3. Align and order to exact columns expected by preprocessor pipeline:
    expected_cols = [
        # Numeric features
        'days_until_event', 'event_hour', 'is_weekend', 'listing_count',
        'section_count', 'section_group_count', 'max_available_lot',
        'avg_max_available_lot', 'deal_rate', 'ga_listing_rate',
        'listing_count_prev', 'listing_change', 'latitude', 'longitude',
        'listing_change_rate', 'listing_ratio', 'listing_pressure',
        'listings_per_section', 'available_per_section',
        'listing_section_ratio', 'deal_pressure',
        # Categorical features
        'day_of_week', 'city', 'state', 'metro', 'timezone',
        'addressCountryCode', 'event_urgency', 'event_time_period'
    ]
    
    df_model_input = df[expected_cols]
    
    return df_model_input
