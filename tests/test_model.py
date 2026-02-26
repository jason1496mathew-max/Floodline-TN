"""
Test suite for ML model validation

Tests:
- Model file existence
- Metrics validation
- F1-score targets
- Prediction functionality
- Feature engineering
- Model inference
"""

import pandas as pd
import pytest
import json
from pathlib import Path
import joblib
import numpy as np


# Paths to model artifacts
MODELS_PATH = Path(__file__).parent.parent / 'models'
MODEL_FILE = MODELS_PATH / 'trained' / 'flood_classifier.pkl'
SCALER_FILE = MODELS_PATH / 'trained' / 'scaler.pkl'
METRICS_FILE = MODELS_PATH / 'metrics' / 'performance.json'
CM_FILE = MODELS_PATH / 'metrics' / 'confusion_matrix.csv'


class TestModelArtifacts:
    """Test if model artifacts exist"""
    
    def test_model_file_exists(self):
        """Check if trained model exists"""
        assert MODEL_FILE.exists(), \
            f"Model not found at {MODEL_FILE}. Run: python models/train.py"
    
    def test_scaler_file_exists(self):
        """Check if feature scaler exists"""
        assert SCALER_FILE.exists(), \
            f"Scaler not found at {SCALER_FILE}"
    
    def test_metrics_file_exists(self):
        """Check if metrics file exists"""
        assert METRICS_FILE.exists(), \
            f"Metrics not found at {METRICS_FILE}"
    
    def test_confusion_matrix_exists(self):
        """Check if confusion matrix CSV exists"""
        assert CM_FILE.exists(), \
            f"Confusion matrix not found at {CM_FILE}"


class TestModelPerformance:
    """Test model performance metrics"""
    
    @pytest.fixture
    def metrics(self):
        """Load performance metrics"""
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    
    def test_f1_score_minimum(self, metrics):
        """Validate F1-score meets minimum threshold"""
        f1 = metrics['metrics']['f1_score_weighted']
        assert f1 >= 0.75, \
            f"F1-score {f1:.4f} below minimum threshold 0.75"
    
    def test_f1_score_target(self, metrics):
        """Check if F1-score meets target (warning if not)"""
        f1 = metrics['metrics']['f1_score_weighted']
        if f1 < 0.80:
            print(f"\n⚠️  Warning: F1-score {f1:.4f} below target 0.80")
    
    def test_precision_reasonable(self, metrics):
        """Check precision is reasonable"""
        precision = metrics['metrics']['precision_weighted']
        assert precision >= 0.70, \
            f"Precision {precision:.4f} too low"
    
    def test_recall_reasonable(self, metrics):
        """Check recall is reasonable"""
        recall = metrics['metrics']['recall_weighted']
        assert recall >= 0.70, \
            f"Recall {recall:.4f} too low"
    
    def test_accuracy_reasonable(self, metrics):
        """Check accuracy is reasonable"""
        accuracy = metrics['metrics']['accuracy']
        assert accuracy >= 0.70, \
            f"Accuracy {accuracy:.4f} too low"
    
    def test_class_metrics_present(self, metrics):
        """Check all class metrics are present"""
        assert 'class_metrics' in metrics
        assert 'low' in metrics['class_metrics']
        assert 'medium' in metrics['class_metrics']
        assert 'high' in metrics['class_metrics']
    
    def test_cross_validation_stable(self, metrics):
        """Check cross-validation scores are stable"""
        if 'cross_validation' in metrics:
            cv_scores = metrics['cross_validation']['cv_scores']
            std = np.std(cv_scores)
            assert std < 0.1, \
                f"CV scores too unstable (std: {std:.4f})"


class TestModelStructure:
    """Test model structure and metadata"""
    
    @pytest.fixture
    def metrics(self):
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    
    def test_model_version_present(self, metrics):
        """Check model version is documented"""
        assert 'model_version' in metrics
        assert metrics['model_version'] is not None
    
    def test_features_documented(self, metrics):
        """Check features are documented"""
        assert 'features' in metrics
        assert len(metrics['features']) > 0
    
    def test_feature_count_reasonable(self, metrics):
        """Check feature count is reasonable"""
        num_features = metrics.get('num_features', len(metrics.get('features', [])))
        assert 10 <= num_features <= 30, \
            f"Unexpected feature count: {num_features}"
    
    def test_training_samples_sufficient(self, metrics):
        """Check sufficient training samples"""
        train_samples = metrics.get('training_samples', 0)
        assert train_samples >= 1000, \
            f"Too few training samples: {train_samples}"
    
    def test_ensemble_weights_present(self, metrics):
        """Check ensemble weights are documented"""
        if 'ensemble_weights' in metrics:
            weights = metrics['ensemble_weights']
            assert 'random_forest' in weights
            assert 'xgboost' in weights
            assert abs(weights['random_forest'] + weights['xgboost'] - 1.0) < 0.01


class TestModelPrediction:
    """Test model prediction functionality"""
    
    def test_model_can_load(self):
        """Test model can be loaded"""
        model = joblib.load(MODEL_FILE)
        assert model is not None
    
    def test_scaler_can_load(self):
        """Test scaler can be loaded"""
        scaler = joblib.load(SCALER_FILE)
        assert scaler is not None
    
    def test_predictor_initialization(self):
        """Test FloodPredictor can initialize"""
        from models.predict import FloodPredictor
        
        predictor = FloodPredictor()
        assert predictor.model is not None
        assert len(predictor.class_names) == 3
    
    def test_single_prediction(self):
        """Test single prediction works"""
        from models.predict import FloodPredictor
        
        predictor = FloodPredictor()
        
        test_data = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Chennai'],
            'rainfall_mm': [150.0],
            'river_level_m': [2.5],
            'soil_moisture': [0.70],
            'humidity_pct': [85.0],
            'reservoir_pct': [70.0],
            'rainfall_7d': [300.0],
            'elevation_m': [7]
        })
        
        result = predictor.predict(test_data)
        
        # Check result structure
        assert 'risk_class' in result
        assert 'risk_class_id' in result
        assert 'probability' in result
        assert 'probabilities' in result
        
        # Check values are valid
        assert result['risk_class'] in ['Low', 'Medium', 'High']
        assert 0 <= result['risk_class_id'] <= 2
        assert 0 <= result['probability'] <= 100
    
    def test_probability_sum(self):
        """Test probabilities sum to 100%"""
        from models.predict import FloodPredictor
        
        predictor = FloodPredictor()
        
        test_data = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Madurai'],
            'rainfall_mm': [100.0],
            'river_level_m': [1.5],
            'soil_moisture': [0.60],
            'humidity_pct': [75.0],
            'reservoir_pct': [60.0],
            'rainfall_7d': [200.0],
            'elevation_m': [134]
        })
        
        result = predictor.predict(test_data)
        
        prob_sum = (
            result['probabilities']['low'] +
            result['probabilities']['medium'] +
            result['probabilities']['high']
        )
        
        assert abs(prob_sum - 100.0) < 0.1, \
            f"Probabilities don't sum to 100: {prob_sum}"
    
    def test_batch_prediction(self):
        """Test batch prediction works"""
        from models.predict import FloodPredictor
        
        predictor = FloodPredictor()
        
        # Create batch of 3 predictions
        test_data = pd.DataFrame({
            'date': ['2023-11-15', '2023-03-10', '2023-10-05'],
            'district': ['Chennai', 'Coimbatore', 'Madurai'],
            'rainfall_mm': [150.0, 20.0, 80.0],
            'river_level_m': [2.5, 0.5, 1.5],
            'soil_moisture': [0.70, 0.35, 0.55],
            'humidity_pct': [85.0, 55.0, 75.0],
            'reservoir_pct': [70.0, 45.0, 60.0],
            'rainfall_7d': [300.0, 50.0, 180.0],
            'elevation_m': [7, 411, 134]
        })
        
        results = predictor.predict_batch(test_data)
        
        assert len(results) == 3
        for result in results:
            assert 'risk_class' in result
            assert result['risk_class'] in ['Low', 'Medium', 'High']


class TestFeatureEngineering:
    """Test feature engineering pipeline"""
    
    def test_feature_engineering_runs(self):
        """Test feature engineering completes without error"""
        from pipeline.feature_engineering import engineer_features
        
        # Create minimal test data
        test_data = pd.DataFrame({
            'date': ['2023-11-15', '2023-11-16'],
            'district': ['Chennai', 'Chennai'],
            'rainfall_mm': [150.0, 120.0],
            'river_level_m': [2.5, 2.3],
            'soil_moisture': [0.70, 0.68],
            'humidity_pct': [85.0, 83.0],
            'reservoir_pct': [70.0, 69.0],
            'rainfall_7d': [300.0, 290.0],
            'elevation_m': [7, 7]
        })
        
        df_eng, feature_cols = engineer_features(test_data, fit_scaler=False)
        
        assert len(feature_cols) > 0
        assert len(df_eng) == 2
    
    def test_feature_names_consistent(self):
        """Test feature names match between training and inference"""
        from pipeline.feature_engineering import get_feature_names
        
        with open(METRICS_FILE, 'r') as f:
            metrics = json.load(f)
        
        expected_features = get_feature_names()
        actual_features = metrics['features']
        
        # Should have same features (order might differ)
        assert set(expected_features) == set(actual_features), \
            "Feature names mismatch between training and inference"
    
    def test_no_nan_after_engineering(self):
        """Test feature engineering produces no NaN values"""
        from pipeline.feature_engineering import engineer_features
        
        test_data = pd.DataFrame({
            'date': ['2023-11-15', '2023-11-16', '2023-11-17'],
            'district': ['Chennai', 'Chennai', 'Chennai'],
            'rainfall_mm': [150.0, 120.0, 100.0],
            'river_level_m': [2.5, 2.3, 2.0],
            'soil_moisture': [0.70, 0.68, 0.65],
            'humidity_pct': [85.0, 83.0, 80.0],
            'reservoir_pct': [70.0, 69.0, 68.0],
            'rainfall_7d': [300.0, 290.0, 280.0],
            'elevation_m': [7, 7, 7]
        })
        
        df_eng, feature_cols = engineer_features(test_data, fit_scaler=False)
        
        # Check for NaN values
        nan_count = df_eng[feature_cols].isna().sum().sum()
        assert nan_count == 0, f"Found {nan_count} NaN values after feature engineering"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_columns_error(self):
        """Test error raised for missing columns"""
        from models.predict import FloodPredictor
        from pipeline.feature_engineering import validate_input_data
        
        incomplete_data = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Chennai'],
            'rainfall_mm': [150.0]
            # Missing other required columns
        })
        
        with pytest.raises(ValueError):
            validate_input_data(incomplete_data)
    
    def test_extreme_values_handled(self):
        """Test model handles extreme input values"""
        from models.predict import FloodPredictor
        
        predictor = FloodPredictor()
        
        # Extreme values
        extreme_data = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Chennai'],
            'rainfall_mm': [500.0],  # Extreme rainfall
            'river_level_m': [8.0],   # Very high river level
            'soil_moisture': [1.0],   # Fully saturated
            'humidity_pct': [100.0],  # Maximum humidity
            'reservoir_pct': [100.0], # Full reservoir
            'rainfall_7d': [1000.0],  # Extreme 7-day rainfall
            'elevation_m': [0]        # Sea level
        })
        
        result = predictor.predict(extreme_data)
        
        # Should still produce valid prediction
        assert result['risk_class'] in ['Low', 'Medium', 'High']
        assert 0 <= result['probability'] <= 100


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
