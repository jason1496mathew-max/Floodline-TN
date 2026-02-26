"""
Flood Risk Prediction Interface

Provides inference API for trained flood classification model.
Handles feature engineering, scaling, and probability predictions.

Usage:
    from models.predict import FloodPredictor
    
    predictor = FloodPredictor()
    
    input_data = pd.DataFrame({
        'date': ['2023-11-15'],
        'district': ['Chennai'],
        'rainfall_mm': [185.0],
        'river_level_m': [3.2],
        'soil_moisture': [0.78],
        'humidity_pct': [89.0],
        'reservoir_pct': [67.0],
        'rainfall_7d': [425.0],
        'elevation_m': [7]
    })
    
    result = predictor.predict(input_data)
    print(f"Risk: {result['risk_class']} ({result['probability']:.1f}%)")
"""

import pandas as pd
import joblib
import json
from pathlib import Path
import sys
import warnings

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.feature_engineering import engineer_features, validate_input_data

warnings.filterwarnings('ignore')


class FloodPredictor:
    """
    Flood risk prediction interface
    
    Attributes:
        model: Trained ensemble classifier
        class_names: List of risk class names ['Low', 'Medium', 'High']
        model_version: Model version string
        feature_names: List of feature names used by model
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize predictor
        
        Args:
            model_path: Optional path to model file. If None, uses default location.
        
        Raises:
            FileNotFoundError: If model file not found
        """
        if model_path is None:
            model_path = Path(__file__).parent / 'trained' / 'flood_classifier.pkl'
        else:
            model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Please run: python models/train.py"
            )
        
        # Load model
        self.model = joblib.load(model_path)
        self.class_names = ['Low', 'Medium', 'High']
        
        # Load metadata if available
        metrics_path = Path(__file__).parent / 'metrics' / 'performance.json'
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
                self.model_version = metrics.get('model_version', 'Unknown')
                self.feature_names = metrics.get('features', [])
        else:
            self.model_version = 'Unknown'
            self.feature_names = []
        
        print(f"✅ FloodPredictor initialized (version: {self.model_version})")
    
    def predict(self, input_data: pd.DataFrame) -> dict:
        """
        Predict flood risk for input data
        
        Args:
            input_data: DataFrame with columns:
                - date, district, rainfall_mm, river_level_m, soil_moisture,
                  humidity_pct, reservoir_pct, rainfall_7d, elevation_m
        
        Returns:
            Dictionary with:
                - risk_class: 'Low', 'Medium', or 'High'
                - risk_class_id: 0, 1, or 2
                - probability: Float 0-100 (confidence in predicted class)
                - probabilities: Dict with all class probabilities
                - raw_score: Risk score before classification
        
        Example:
            >>> result = predictor.predict(df)
            >>> print(result['risk_class'])
            'High'
            >>> print(result['probability'])
            87.3
        """
        # Validate input
        validate_input_data(input_data)
        
        # Engineer features
        input_eng, feature_cols = engineer_features(input_data, fit_scaler=False)
        X = input_eng[feature_cols]
        
        # Predict
        risk_class_id = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get risk class name
        risk_class = self.class_names[risk_class_id]
        
        # Calculate overall risk probability (weighted sum)
        risk_score = (
            probabilities[0] * 0 +      # Low = 0%
            probabilities[1] * 50 +     # Medium = 50%
            probabilities[2] * 100      # High = 100%
        )
        
        return {
            "risk_class": risk_class,
            "risk_class_id": int(risk_class_id),
            "probability": float(probabilities[risk_class_id] * 100),
            "probabilities": {
                "low": float(probabilities[0] * 100),
                "medium": float(probabilities[1] * 100),
                "high": float(probabilities[2] * 100)
            },
            "raw_score": float(risk_score)
        }
    
    def predict_batch(self, input_data: pd.DataFrame) -> list:
        """
        Predict flood risk for multiple records
        
        Args:
            input_data: DataFrame with multiple rows
        
        Returns:
            List of prediction dictionaries
        """
        # Validate input
        validate_input_data(input_data)
        
        # Engineer features
        input_eng, feature_cols = engineer_features(input_data, fit_scaler=False)
        X = input_eng[feature_cols]
        
        # Predict
        risk_class_ids = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Format results
        results = []
        for i in range(len(X)):
            risk_class_id = risk_class_ids[i]
            class_proba = probabilities[i]
            
            risk_score = (
                class_proba[0] * 0 +
                class_proba[1] * 50 +
                class_proba[2] * 100
            )
            
            results.append({
                "risk_class": self.class_names[risk_class_id],
                "risk_class_id": int(risk_class_id),
                "probability": float(class_proba[risk_class_id] * 100),
                "probabilities": {
                    "low": float(class_proba[0] * 100),
                    "medium": float(class_proba[1] * 100),
                    "high": float(class_proba[2] * 100)
                },
                "raw_score": float(risk_score)
            })
        
        return results
    
    def get_model_info(self) -> dict:
        """
        Get model metadata
        
        Returns:
            Dictionary with model information
        """
        metrics_path = Path(__file__).parent / 'metrics' / 'performance.json'
        
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                return json.load(f)
        else:
            return {
                "model_version": self.model_version,
                "error": "Metrics file not found"
            }


def predict_for_district(
    district_name: str,
    date: str,
    rainfall_mm: float,
    river_level_m: float,
    soil_moisture: float,
    humidity_pct: float,
    reservoir_pct: float,
    rainfall_7d: float,
    elevation_m: float
) -> dict:
    """
    Convenience function for single district prediction
    
    Args:
        All flood parameters for one district
    
    Returns:
        Prediction dictionary
    """
    predictor = FloodPredictor()
    
    input_data = pd.DataFrame({
        'date': [date],
        'district': [district_name],
        'rainfall_mm': [rainfall_mm],
        'river_level_m': [river_level_m],
        'soil_moisture': [soil_moisture],
        'humidity_pct': [humidity_pct],
        'reservoir_pct': [reservoir_pct],
        'rainfall_7d': [rainfall_7d],
        'elevation_m': [elevation_m]
    })
    
    return predictor.predict(input_data)


# CLI interface for testing
if __name__ == "__main__":
    print("🔮 Flood Risk Predictor - Test Mode")
    print("=" * 60)
    
    try:
        # Initialize predictor
        predictor = FloodPredictor()
        
        print()
        print("📊 Model Information:")
        info = predictor.get_model_info()
        print(f"   Version: {info.get('model_version', 'Unknown')}")
        print(f"   Features: {info.get('num_features', 'Unknown')}")
        if 'metrics' in info:
            print(f"   F1-Score: {info['metrics'].get('f1_score_weighted', 0):.4f}")
        
        print()
        print("🧪 Test Case 1: High Risk Scenario")
        print("   (Heavy rainfall in low-lying coastal district)")
        
        # Test 1: High risk
        test_data_high = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Chennai'],
            'rainfall_mm': [185.0],
            'river_level_m': [3.2],
            'soil_moisture': [0.78],
            'humidity_pct': [89.0],
            'reservoir_pct': [67.0],
            'rainfall_7d': [425.0],
            'elevation_m': [7]
        })
        
        result = predictor.predict(test_data_high)
        
        print(f"\n   🚨 Prediction: {result['risk_class']}")
        print(f"   Confidence: {result['probability']:.2f}%")
        print(f"   Risk Score: {result['raw_score']:.1f}/100")
        print(f"   Probabilities:")
        print(f"      Low: {result['probabilities']['low']:.2f}%")
        print(f"      Medium: {result['probabilities']['medium']:.2f}%")
        print(f"      High: {result['probabilities']['high']:.2f}%")
        
        print()
        print("🧪 Test Case 2: Low Risk Scenario")
        print("   (Normal conditions in elevated district)")
        
        # Test 2: Low risk
        test_data_low = pd.DataFrame({
            'date': ['2023-03-10'],
            'district': ['Coimbatore'],
            'rainfall_mm': [12.0],
            'river_level_m': [0.5],
            'soil_moisture': [0.35],
            'humidity_pct': [55.0],
            'reservoir_pct': [45.0],
            'rainfall_7d': [35.0],
            'elevation_m': [411]
        })
        
        result = predictor.predict(test_data_low)
        
        print(f"\n   ✅ Prediction: {result['risk_class']}")
        print(f"   Confidence: {result['probability']:.2f}%")
        print(f"   Risk Score: {result['raw_score']:.1f}/100")
        print(f"   Probabilities:")
        print(f"      Low: {result['probabilities']['low']:.2f}%")
        print(f"      Medium: {result['probabilities']['medium']:.2f}%")
        print(f"      High: {result['probabilities']['high']:.2f}%")
        
        print()
        print("🧪 Test Case 3: Medium Risk Scenario")
        print("   (Moderate rainfall, elevated soil moisture)")
        
        # Test 3: Medium risk
        test_data_medium = pd.DataFrame({
            'date': ['2023-10-05'],
            'district': ['Madurai'],
            'rainfall_mm': [75.0],
            'river_level_m': [1.8],
            'soil_moisture': [0.62],
            'humidity_pct': [78.0],
            'reservoir_pct': [58.0],
            'rainfall_7d': [180.0],
            'elevation_m': [134]
        })
        
        result = predictor.predict(test_data_medium)
        
        print(f"\n   ⚠️  Prediction: {result['risk_class']}")
        print(f"   Confidence: {result['probability']:.2f}%")
        print(f"   Risk Score: {result['raw_score']:.1f}/100")
        print(f"   Probabilities:")
        print(f"      Low: {result['probabilities']['low']:.2f}%")
        print(f"      Medium: {result['probabilities']['medium']:.2f}%")
        print(f"      High: {result['probabilities']['high']:.2f}%")
        
        print()
        print("=" * 60)
        print("✅ All test cases completed successfully!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease run:")
        print("  python models/train.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
