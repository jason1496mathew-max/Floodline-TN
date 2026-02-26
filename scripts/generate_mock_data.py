"""
Floodline TN - Mock Data Generator (Sub-Agent 1A)

Generates realistic synthetic flood data for 38 Tamil Nadu districts
covering 8 years (2016-2023) with daily granularity.

Models:
- Monsoon seasonality (SW and NE monsoons)
- Historical flood events (2015 Chennai, 2018 Gaja, etc.)
- Parameter correlations (rainfall→river level, soil moisture, etc.)
- Realistic noise and missing value patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Set random seed for reproducibility
np.random.seed(42)

# Load district metadata
config_path = Path(__file__).parent.parent / 'config' / 'districts.json'
with open(config_path, encoding='utf-8') as f:
    DISTRICTS = json.load(f)['districts']

# Historical flood events to inject
HISTORICAL_EVENTS = [
    {
        "date_range": ("2015-11-01", "2015-12-15"),
        "affected_districts": ["Chennai", "Kanchipuram", "Tiruvallur", "Cuddalore"],
        "rainfall_spike": 2.5,
        "description": "2015 Chennai floods"
    },
    {
        "date_range": ("2018-11-10", "2018-11-20"),
        "affected_districts": ["Thanjavur", "Tiruvarur", "Nagapattinam", "Pudukkottai"],
        "rainfall_spike": 2.2,
        "description": "Cyclone Gaja"
    },
    {
        "date_range": ("2021-11-08", "2021-11-12"),
        "affected_districts": ["Chennai", "Chengalpattu", "Viluppuram"],
        "rainfall_spike": 1.8,
        "description": "November 2021 floods"
    },
    {
        "date_range": ("2023-12-04", "2023-12-08"),
        "affected_districts": ["Chennai", "Tiruvallur", "Kanchipuram"],
        "rainfall_spike": 2.3,
        "description": "Cyclone Michaung"
    }
]


def monsoon_multiplier(month: int) -> float:
    """
    Returns rainfall multiplier based on monsoon seasons.
    
    SW Monsoon: June-September (moderate for TN)
    NE Monsoon: October-December (peak for TN)
    """
    multipliers = {
        1: 0.2,   # January - dry
        2: 0.2,   # February - dry
        3: 0.3,   # March - pre-monsoon
        4: 0.4,   # April - summer
        5: 0.5,   # May - pre-monsoon
        6: 1.2,   # June - SW monsoon
        7: 1.3,   # July - SW monsoon
        8: 1.2,   # August - SW monsoon
        9: 1.0,   # September - monsoon end
        10: 1.8,  # October - NE monsoon (peak for TN)
        11: 2.0,  # November - NE monsoon (peak)
        12: 1.5   # December - NE monsoon
    }
    return multipliers[month]


def generate_base_rainfall(date: datetime, base_mean: float = 50.0) -> float:
    """
    Generate rainfall with seasonal variation.
    
    Uses log-normal distribution to simulate realistic rainfall patterns
    (many low-rainfall days, occasional extreme events).
    """
    month_mult = monsoon_multiplier(date.month)
    daily_mean = base_mean * month_mult
    
    # Log-normal distribution for rainfall (skewed right)
    rainfall = np.random.lognormal(mean=np.log(daily_mean + 1), sigma=0.8)
    
    # Cap at 400mm (extreme event threshold)
    return min(rainfall, 400.0)


def apply_historical_event(df: pd.DataFrame, event: dict) -> pd.DataFrame:
    """
    Inject historical event patterns into the dataset.
    
    Increases rainfall for affected districts during event period
    and flags flood occurrence.
    """
    start = pd.to_datetime(event["date_range"][0])
    end = pd.to_datetime(event["date_range"][1])
    
    mask = (
        (df['date'] >= start) & 
        (df['date'] <= end) & 
        (df['district'].isin(event["affected_districts"]))
    )
    
    # Spike rainfall during event
    df.loc[mask, 'rainfall_mm'] *= event["rainfall_spike"]
    
    # Force flood flag for historical events
    df.loc[mask, 'flood_occurred'] = 1
    
    print(f"  ✓ Injected: {event['description']} ({start.date()} to {end.date()})")
    
    return df


def correlate_parameters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add realistic correlations between parameters.
    
    - River level lags rainfall (6-hour effect)
    - Soil moisture builds with cumulative rainfall
    - Humidity increases with rainfall
    - Reservoir levels depend on seasonal patterns
    """
    print("  Computing parameter correlations...")
    
    # Sort by district and date for rolling calculations
    df = df.sort_values(['district', 'date']).reset_index(drop=True)
    
    # River level: 3-day rolling mean of rainfall (lagged effect)
    df['river_level_m'] = (
        df.groupby('district')['rainfall_mm']
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(drop=True) / 80.0  # Scaling factor
        - 1.0  # Baseline below danger mark
    )
    
    # Soil moisture: 5-day rolling mean (saturation effect)
    df['soil_moisture'] = np.clip(
        df.groupby('district')['rainfall_mm']
        .rolling(window=5, min_periods=1)
        .mean()
        .reset_index(drop=True) / 150.0,
        0.0, 1.0
    )
    
    # Humidity: correlates with daily rainfall + random noise
    df['humidity_pct'] = np.clip(
        60 + (df['rainfall_mm'] / 5.0) + np.random.normal(0, 5, len(df)),
        30, 100
    )
    
    # Reservoir storage: depletes in dry season, fills in monsoon
    is_dry_season = df['date'].dt.month.isin([4, 5])
    df['reservoir_pct'] = np.clip(
        50 + (df['rainfall_7d'] / 10.0) - (is_dry_season * 15),
        10, 95
    )
    
    return df


def label_flood_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determine flood_occurred based on multiple thresholds.
    
    Flood conditions:
    - Extreme rainfall (>150mm)
    - High river level (>2.5m above danger)
    - Saturated soil + heavy cumulative rain
    - Reservoir overflow risk (>90%)
    """
    print("  Labeling flood events...")
    
    conditions = (
        (df['rainfall_mm'] > 150) |  # Extreme rainfall
        (df['river_level_m'] > 2.5) |  # River flooding
        ((df['rainfall_7d'] > 250) & (df['soil_moisture'] > 0.75)) |  # Saturated soil
        (df['reservoir_pct'] > 90)  # Reservoir overflow risk
    )
    
    df.loc[conditions, 'flood_occurred'] = 1
    
    # Add realistic noise (5% false negatives, 3% false positives)
    noise_mask = np.random.rand(len(df))
    df.loc[(df['flood_occurred'] == 1) & (noise_mask < 0.05), 'flood_occurred'] = 0
    df.loc[(df['flood_occurred'] == 0) & (noise_mask > 0.97), 'flood_occurred'] = 1
    
    return df


def inject_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add realistic missing value patterns (3-5% MCAR).
    
    Simulates sensor failures, transmission errors, etc.
    """
    print("  Injecting missing values...")
    
    target_columns = ['rainfall_mm', 'humidity_pct', 'reservoir_pct']
    
    for col in target_columns:
        missing_rate = np.random.uniform(0.03, 0.05)
        missing_mask = np.random.rand(len(df)) < missing_rate
        df.loc[missing_mask, col] = np.nan
        missing_count = missing_mask.sum()
        print(f"    {col}: {missing_count:,} missing ({missing_count/len(df)*100:.2f}%)")
    
    return df


def generate_mock_flood_data():
    """
    Main function to generate 8 years of synthetic flood data
    for all 38 Tamil Nadu districts.
    
    Returns:
        pd.DataFrame: Generated dataset
    """
    print("🌊 Floodline TN - Mock Data Generator (Sub-Agent 1A)")
    print("=" * 60)
    print(f"Generating data for {len(DISTRICTS)} districts (2016-2023)...")
    print()
    
    # Date range: 2016-01-01 to 2023-12-31
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Days: {len(date_range):,}")
    print(f"Expected rows: {len(DISTRICTS) * len(date_range):,}")
    print()
    
    # Generate base dataset
    print("Step 1: Generating base rainfall data...")
    data = []
    
    for district in DISTRICTS:
        for date in date_range:
            row = {
                'date': date,
                'district': district['name'],
                'elevation_m': district['elevation_m'],
                'rainfall_mm': generate_base_rainfall(date),
                'river_level_m': 0.0,  # Will be computed
                'soil_moisture': 0.0,   # Will be computed
                'humidity_pct': 0.0,    # Will be computed
                'reservoir_pct': 50.0,  # Will be computed
                'rainfall_7d': 0.0,     # Will be computed
                'flood_occurred': 0
            }
            data.append(row)
    
    df = pd.DataFrame(data)
    print(f"  ✓ Generated {len(df):,} rows")
    print()
    
    # Compute 7-day rolling rainfall
    print("Step 2: Computing 7-day rolling rainfall...")
    df = df.sort_values(['district', 'date']).reset_index(drop=True)
    df['rainfall_7d'] = df.groupby('district')['rainfall_mm'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum()
    )
    print("  ✓ Complete")
    print()
    
    # Add parameter correlations
    print("Step 3: Adding parameter correlations...")
    df = correlate_parameters(df)
    print("  ✓ Complete")
    print()
    
    # Inject historical events
    print("Step 4: Injecting historical flood events...")
    for event in HISTORICAL_EVENTS:
        df = apply_historical_event(df, event)
    print("  ✓ Complete")
    print()
    
    # Label flood events
    print("Step 5: Labeling flood events...")
    df = label_flood_events(df)
    flood_count = int(df['flood_occurred'].sum())
    flood_pct = (flood_count / len(df)) * 100
    print(f"  ✓ Total flood events: {flood_count:,} ({flood_pct:.2f}%)")
    print()
    
    # Inject missing values
    print("Step 6: Injecting missing values...")
    df = inject_missing_values(df)
    print("  ✓ Complete")
    print()
    
    # Save to CSV
    print("Step 7: Saving dataset...")
    output_path = Path(__file__).parent.parent / 'data' / 'mock' / 'tn_flood_data.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False, float_format='%.2f')
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved to: {output_path}")
    print(f"  ✓ File size: {file_size_mb:.2f} MB")
    print()
    
    # Generate report
    print("Step 8: Generating report...")
    report = {
        "total_rows": len(df),
        "districts": len(DISTRICTS),
        "date_range": {
            "start": start_date.date().isoformat(),
            "end": end_date.date().isoformat(),
            "days": len(date_range)
        },
        "flood_events": {
            "count": flood_count,
            "percentage": round(flood_pct, 2)
        },
        "missing_values": {
            col: int(df[col].isnull().sum())
            for col in df.columns
        },
        "statistics": {
            "rainfall_mm": {
                "mean": round(df['rainfall_mm'].mean(), 2),
                "std": round(df['rainfall_mm'].std(), 2),
                "max": round(df['rainfall_mm'].max(), 2)
            },
            "river_level_m": {
                "mean": round(df['river_level_m'].mean(), 2),
                "max": round(df['river_level_m'].max(), 2)
            }
        },
        "generated_at": datetime.now().isoformat(),
        "generator_version": "1.0.0"
    }
    
    report_path = Path(__file__).parent.parent / 'data' / 'mock' / 'generation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✓ Report saved to: {report_path}")
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Mock Data Generation Complete!")
    print()
    print(f"📊 Summary:")
    print(f"  • Total rows: {len(df):,}")
    print(f"  • Districts: {len(DISTRICTS)}")
    print(f"  • Date range: {start_date.date()} to {end_date.date()}")
    print(f"  • Flood events: {flood_count:,} ({flood_pct:.2f}%)")
    print(f"  • File size: {file_size_mb:.2f} MB")
    print()
    print("🔄 Next Steps:")
    print("  1. Run validation: python -m pytest tests/test_mock_data.py")
    print("  2. Proceed to Module 03: GeoJSON Pipeline")
    print()
    
    return df


if __name__ == "__main__":
    try:
        df = generate_mock_flood_data()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
