"""
Feature Engineering Pipeline

Transforms raw flood data into ML-ready features with:
- Rolling statistics (7-day rainfall, 3-day river levels)
- Interaction features (rainfall × soil moisture)
- Lag features (previous day rainfall)
- Seasonal indicators (monsoon flag)
- Robust scaling (handles outliers)

Used by: models/train.py, models/predict.py
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from pathlib import Path
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def engineer_features(df: pd.DataFrame, fit_scaler: bool = True) -> tuple:
    """
    Create derived features and normalize
    
    Args:
        df: Raw flood data with columns:
            - date, district, rainfall_mm, river_level_m, soil_moisture,
              humidity_pct, reservoir_pct, rainfall_7d, elevation_m
        fit_scaler: If True, fit new scaler; if False, use existing saved scaler
    
    Returns:
        Tuple of (DataFrame with engineered features, list of feature column names)
    
    Example:
        >>> df = pd.read_csv('data/mock/tn_flood_data.csv')
        >>> df_eng, features = engineer_features(df, fit_scaler=True)
        >>> print(f"Engineered {len(features)} features")
    """
    df = df.copy()
    
    print("🔧 Engineering features...")
    
    # Ensure date is datetime
    if 'date' not in df.columns:
        raise ValueError("DataFrame must have 'date' column")
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by district and date for rolling calculations
    df = df.sort_values(['district', 'date']).reset_index(drop=True)
    
    # ========================================
    # 1. ROLLING STATISTICS
    # ========================================
    print("   📊 Computing rolling statistics...")
    
    # 3-day rolling average river level
    df['river_level_3d_avg'] = df.groupby('district')['river_level_m'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # 3-day rolling average rainfall
    df['rainfall_3d_avg'] = df.groupby('district')['rainfall_mm'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # ========================================
    # 2. INTERACTION FEATURES
    # ========================================
    print("   🔗 Creating interaction features...")
    
    # Rainfall × Soil moisture (saturation effect)
    df['rainfall_x_soil'] = df['rainfall_mm'] * df['soil_moisture']
    
    # River level / Elevation (normalized flood risk)
    df['river_x_elevation'] = df['river_level_m'] / (df['elevation_m'] + 1)  # +1 to avoid division by zero
    
    # Humidity × Soil moisture (moisture accumulation)
    df['humidity_x_soil'] = (df['humidity_pct'] / 100) * df['soil_moisture']
    
    # ========================================
    # 3. LAG FEATURES
    # ========================================
    print("   ⏱️  Creating lag features...")
    
    # Yesterday's rainfall
    df['rainfall_lag1'] = df.groupby('district')['rainfall_mm'].shift(1).fillna(0)
    
    # Yesterday's river level
    df['river_level_lag1'] = df.groupby('district')['river_level_m'].shift(1).fillna(0)
    
    # ========================================
    # 4. TEMPORAL FEATURES
    # ========================================
    print("   📅 Extracting temporal features...")
    
    # Monsoon season flag (June-December)
    df['is_monsoon'] = df['date'].dt.month.isin([6, 7, 8, 9, 10, 11, 12]).astype(int)
    
    # Month as cyclic feature (useful for seasonality)
    df['month_sin'] = np.sin(2 * np.pi * df['date'].dt.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['date'].dt.month / 12)
    
    # ========================================
    # 5. DERIVED RISK INDICATORS
    # ========================================
    print("   ⚠️  Computing risk indicators...")
    
    # Cumulative 7-day rainfall intensity
    df['rainfall_7d_intensity'] = df['rainfall_7d'] / 7  # Average daily rainfall over week
    
    # Reservoir overflow risk (reservoir % × rainfall)
    df['reservoir_overflow_risk'] = (df['reservoir_pct'] / 100) * df['rainfall_mm']
    
    # ========================================
    # 6. HANDLE MISSING VALUES
    # ========================================
    print("   🔍 Handling missing values...")
    
    # Define feature columns
    feature_cols = [
        # Base features
        'rainfall_mm', 'river_level_m', 'soil_moisture', 'humidity_pct',
        'reservoir_pct', 'rainfall_7d', 'elevation_m',
        
        # Rolling features
        'river_level_3d_avg', 'rainfall_3d_avg',
        
        # Interaction features
        'rainfall_x_soil', 'river_x_elevation', 'humidity_x_soil',
        
        # Lag features
        'rainfall_lag1', 'river_level_lag1',
        
        # Temporal features
        'is_monsoon', 'month_sin', 'month_cos',
        
        # Derived features
        'rainfall_7d_intensity', 'reservoir_overflow_risk'
    ]
    
    # Fill missing values with median (robust to outliers)
    for col in feature_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
        else:
            print(f"   ⚠️  Warning: Column {col} not found, skipping")
    
    # ========================================
    # 7. FEATURE SCALING
    # ========================================
    print("   📏 Scaling features...")
    
    scaler_path = Path(__file__).parent.parent / 'models' / 'trained' / 'scaler.pkl'
    
    if fit_scaler:
        # Fit new scaler on training data
        scaler = RobustScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
        
        # Save scaler for inference
        scaler_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, scaler_path)
        print(f"   ✅ Fitted and saved scaler to {scaler_path}")
    else:
        # Load existing scaler for inference
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            df[feature_cols] = scaler.transform(df[feature_cols])
            print(f"   ✅ Loaded scaler from {scaler_path}")
        else:
            print(f"   ⚠️  Warning: Scaler not found at {scaler_path}, skipping scaling")
    
    print(f"   ✅ Engineered {len(feature_cols)} features")
    
    return df, feature_cols


def get_feature_names() -> list:
    """
    Get list of feature names used in the model
    
    Returns:
        List of feature column names
    """
    return [
        'rainfall_mm', 'river_level_m', 'soil_moisture', 'humidity_pct',
        'reservoir_pct', 'rainfall_7d', 'elevation_m',
        'river_level_3d_avg', 'rainfall_3d_avg',
        'rainfall_x_soil', 'river_x_elevation', 'humidity_x_soil',
        'rainfall_lag1', 'river_level_lag1',
        'is_monsoon', 'month_sin', 'month_cos',
        'rainfall_7d_intensity', 'reservoir_overflow_risk'
    ]


def validate_input_data(df: pd.DataFrame) -> bool:
    """
    Validate input data has required columns
    
    Args:
        df: Input DataFrame
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    required_cols = [
        'date', 'district', 'rainfall_mm', 'river_level_m', 'soil_moisture',
        'humidity_pct', 'reservoir_pct', 'rainfall_7d', 'elevation_m'
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return True


# CLI interface for testing
if __name__ == "__main__":
    print("🔧 Feature Engineering Pipeline - Test Mode")
    print("=" * 60)
    
    # Load mock data
    data_path = Path(__file__).parent.parent / 'data' / 'mock' / 'tn_flood_data.csv'
    
    if not data_path.exists():
        print(f"❌ Error: Mock data not found at {data_path}")
        print("   Run: python scripts/generate_mock_data.py")
        exit(1)
    
    print(f"\n📊 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df):,} records")
    
    # Validate input
    try:
        validate_input_data(df)
        print("   ✅ Input data validated")
    except ValueError as e:
        print(f"   ❌ Validation error: {e}")
        exit(1)
    
    print()
    
    # Engineer features
    df_eng, feature_cols = engineer_features(df, fit_scaler=True)
    
    print()
    print("=" * 60)
    print("📋 Feature Engineering Summary:")
    print(f"   Total features: {len(feature_cols)}")
    print(f"   Output shape: {df_eng[feature_cols].shape}")
    print()
    print("📊 Sample engineered features (first 3 rows):")
    print(df_eng[feature_cols].head(3).to_string())
    print()
    print("📈 Feature statistics:")
    print(df_eng[feature_cols].describe().loc[['mean', 'std', 'min', 'max']].round(3).to_string())
    print()
    print("=" * 60)
    print("✅ Feature engineering test complete!")
