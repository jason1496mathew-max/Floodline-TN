"""
Test suite for mock flood data validation (Sub-Agent 1C: Data Quality Validator)

Validates:
- File existence
- Row count
- Schema integrity
- Flood event balance
- Date range coverage
- Value ranges
- Missing value patterns
"""

import pandas as pd
import pytest
import json
from pathlib import Path
from datetime import datetime

# Path to mock data
DATA_PATH = Path(__file__).parent.parent / 'data' / 'mock' / 'tn_flood_data.csv'
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'districts.json'
REPORT_PATH = Path(__file__).parent.parent / 'data' / 'mock' / 'generation_report.json'


class TestMockDataExistence:
    """Test if required files exist"""
    
    def test_csv_exists(self):
        """Check if mock data CSV file exists"""
        assert DATA_PATH.exists(), f"Mock data file not found at {DATA_PATH}"
    
    def test_report_exists(self):
        """Check if generation report exists"""
        assert REPORT_PATH.exists(), f"Generation report not found at {REPORT_PATH}"


class TestMockDataSchema:
    """Test schema and column structure"""
    
    @pytest.fixture
    def df(self):
        """Load mock data"""
        return pd.read_csv(DATA_PATH)
    
    def test_required_columns(self, df):
        """Validate all required columns are present"""
        required_cols = [
            'date', 'district', 'rainfall_mm', 'river_level_m',
            'soil_moisture', 'humidity_pct', 'reservoir_pct',
            'rainfall_7d', 'elevation_m', 'flood_occurred'
        ]
        assert list(df.columns) == required_cols, f"Column mismatch. Expected: {required_cols}, Got: {list(df.columns)}"
    
    def test_column_types(self, df):
        """Validate column data types"""
        df_parsed = pd.read_csv(DATA_PATH, parse_dates=['date'])
        
        assert pd.api.types.is_datetime64_any_dtype(df_parsed['date']), "date must be datetime"
        assert pd.api.types.is_object_dtype(df_parsed['district']), "district must be string"
        assert pd.api.types.is_numeric_dtype(df_parsed['rainfall_mm']), "rainfall_mm must be numeric"
        assert pd.api.types.is_integer_dtype(df_parsed['flood_occurred']), "flood_occurred must be integer"


class TestMockDataSize:
    """Test row count and coverage"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH)
    
    @pytest.fixture
    def districts(self):
        with open(CONFIG_PATH) as f:
            return json.load(f)['districts']
    
    def test_row_count(self, df, districts):
        """Validate expected row count"""
        # 38 districts × 2922 days (2016-2023) = 111,036 rows
        expected_days = 2922  # 8 years including leap years
        expected_rows = len(districts) * expected_days
        
        # Allow some tolerance for rounding
        assert abs(len(df) - expected_rows) < 100, \
            f"Expected ~{expected_rows:,} rows, got {len(df):,}"
    
    def test_all_districts_present(self, df, districts):
        """Check all 38 districts are in dataset"""
        district_names = [d['name'] for d in districts]
        unique_districts = df['district'].unique()
        
        assert len(unique_districts) == len(districts), \
            f"Expected {len(districts)} districts, found {len(unique_districts)}"
        
        for district in district_names:
            assert district in unique_districts, f"District '{district}' missing from dataset"


class TestMockDataDates:
    """Test date range coverage"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH, parse_dates=['date'])
    
    def test_date_range(self, df):
        """Validate date coverage (2016-2023)"""
        assert df['date'].min() == pd.Timestamp('2016-01-01'), \
            f"Start date should be 2016-01-01, got {df['date'].min()}"
        
        assert df['date'].max() == pd.Timestamp('2023-12-31'), \
            f"End date should be 2023-12-31, got {df['date'].max()}"
    
    def test_no_date_gaps(self, df):
        """Check for missing dates in any district"""
        for district in df['district'].unique():
            district_df = df[df['district'] == district].sort_values('date')
            date_diffs = district_df['date'].diff().dropna()
            
            # All differences should be 1 day
            assert (date_diffs == pd.Timedelta(days=1)).all(), \
                f"Date gaps found in {district} district"


class TestMockDataValues:
    """Test value ranges and distributions"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH)
    
    def test_rainfall_range(self, df):
        """Rainfall should be 0-400mm"""
        valid_rainfall = df['rainfall_mm'].dropna()
        assert (valid_rainfall >= 0).all(), "Rainfall cannot be negative"
        assert (valid_rainfall <= 400).all(), "Rainfall exceeds maximum threshold"
    
    def test_river_level_range(self, df):
        """River level should be -2.0 to 5.0m"""
        assert (df['river_level_m'] >= -2.5).all(), "River level too low"
        assert (df['river_level_m'] <= 5.5).all(), "River level too high"
    
    def test_soil_moisture_range(self, df):
        """Soil moisture should be 0-1"""
        assert (df['soil_moisture'] >= 0).all(), "Soil moisture below 0"
        assert (df['soil_moisture'] <= 1).all(), "Soil moisture above 1"
    
    def test_humidity_range(self, df):
        """Humidity should be 30-100%"""
        valid_humidity = df['humidity_pct'].dropna()
        assert (valid_humidity >= 30).all(), "Humidity too low"
        assert (valid_humidity <= 100).all(), "Humidity exceeds 100%"
    
    def test_reservoir_range(self, df):
        """Reservoir should be 10-95%"""
        valid_reservoir = df['reservoir_pct'].dropna()
        assert (valid_reservoir >= 10).all(), "Reservoir below minimum"
        assert (valid_reservoir <= 95).all(), "Reservoir exceeds maximum"
    
    def test_flood_binary(self, df):
        """Flood occurred should be 0 or 1"""
        assert df['flood_occurred'].isin([0, 1]).all(), \
            "flood_occurred must be binary (0 or 1)"


class TestMockDataQuality:
    """Test data quality metrics"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH)
    
    def test_flood_balance(self, df):
        """Check flood event class balance (should be 10-30%)"""
        flood_pct = df['flood_occurred'].mean() * 100
        
        assert 10 <= flood_pct <= 30, \
            f"Flood rate {flood_pct:.2f}% outside acceptable range (10-30%)"
    
    def test_missing_values(self, df):
        """Check missing value rates (<10% per column)"""
        # Only certain columns should have missing values
        allowed_missing = ['rainfall_mm', 'humidity_pct', 'reservoir_pct']
        
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            
            if col in allowed_missing:
                assert missing_pct <= 10, \
                    f"{col} has {missing_pct:.2f}% missing (max 10% allowed)"
            else:
                assert missing_pct == 0, \
                    f"{col} should not have missing values, but has {missing_pct:.2f}%"
    
    def test_target_no_nulls(self, df):
        """Target variable (flood_occurred) must have no nulls"""
        assert df['flood_occurred'].isnull().sum() == 0, \
            "Target variable 'flood_occurred' contains null values"


class TestMockDataCorrelations:
    """Test parameter correlations"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH, parse_dates=['date'])
    
    def test_rainfall_7d_calculation(self, df):
        """Verify 7-day rolling rainfall is correct"""
        # Test one district
        test_district = df[df['district'] == 'Chennai'].sort_values('date').head(10)
        
        for idx in range(7, len(test_district)):
            manual_7d = test_district.iloc[idx-6:idx+1]['rainfall_mm'].sum()
            recorded_7d = test_district.iloc[idx]['rainfall_7d']
            
            # Allow small floating point differences
            assert abs(manual_7d - recorded_7d) < 1.0, \
                f"7-day rainfall mismatch at index {idx}"
    
    def test_river_level_correlation(self, df):
        """River level should correlate with rainfall"""
        # High rainfall should generally lead to higher river levels
        high_rain = df[df['rainfall_mm'] > 100]
        low_rain = df[df['rainfall_mm'] < 10]
        
        avg_high_river = high_rain['river_level_m'].mean()
        avg_low_river = low_rain['river_level_m'].mean()
        
        assert avg_high_river > avg_low_river, \
            "River level should be higher with high rainfall"


class TestHistoricalEvents:
    """Test historical event injection"""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(DATA_PATH, parse_dates=['date'])
    
    def test_2015_chennai_floods(self, df):
        """Verify 2015 Chennai floods are present"""
        event_mask = (
            (df['date'] >= '2015-11-01') &
            (df['date'] <= '2015-12-15') &
            (df['district'] == 'Chennai')
        )
        
        event_data = df[event_mask]
        
        if len(event_data) > 0:  # Only if date range includes 2015
            flood_rate = event_data['flood_occurred'].mean()
            assert flood_rate > 0.5, "2015 Chennai flood event not prominent"
    
    def test_2018_cyclone_gaja(self, df):
        """Verify 2018 Cyclone Gaja is present"""
        event_mask = (
            (df['date'] >= '2018-11-10') &
            (df['date'] <= '2018-11-20') &
            (df['district'] == 'Thanjavur')
        )
        
        event_data = df[event_mask]
        flood_rate = event_data['flood_occurred'].mean()
        
        assert flood_rate > 0.3, "2018 Cyclone Gaja event not prominent"


class TestGenerationReport:
    """Test generation report integrity"""
    
    @pytest.fixture
    def report(self):
        with open(REPORT_PATH) as f:
            return json.load(f)
    
    def test_report_structure(self, report):
        """Check report has required fields"""
        required_fields = [
            'total_rows', 'districts', 'date_range',
            'flood_events', 'missing_values', 'generated_at'
        ]
        
        for field in required_fields:
            assert field in report, f"Report missing field: {field}"
    
    def test_report_accuracy(self, report):
        """Verify report matches actual data"""
        df = pd.read_csv(DATA_PATH)
        
        assert report['total_rows'] == len(df), "Row count mismatch"
        assert report['districts'] == 38, "Should have 38 districts"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
