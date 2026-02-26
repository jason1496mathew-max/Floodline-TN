"""
SHAP Explainability Pipeline for Floodline TN
==============================================

Sub-Agent: 2B (XAI Engineer)
Module: 06 - SHAP Explainer

This module generates SHAP (SHapley Additive exPlanations) values to provide
transparent, interpretable explanations of flood risk predictions.

Outputs:
    - models/trained/shap_explainer.pkl (TreeExplainer)
    - models/trained/shap_feature_names.json (Feature metadata)
    - models/shap/district_explanations.json (Pre-computed explanations)
    - models/shap/global_summary.png (Global feature importance)
    - models/shap/waterfall_example.png (Example waterfall chart)
    - models/shap/shap_report.json (Summary report)

Dependencies:
    - Module 05 (ML Model Training) complete
    - shap, matplotlib, pandas, numpy, joblib

Usage:
    python models/shap_explain.py
"""

import pandas as pd
import numpy as np
import joblib
import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append('.')
from pipeline.feature_engineering import engineer_features


def train_shap_explainer():
    """
    Train SHAP TreeExplainer on the trained ensemble model
    
    Returns:
        tuple: (explainer, X_sample, feature_cols)
    
    Raises:
        FileNotFoundError: If model not found
    """
    print("🧠 Training SHAP Explainer for Floodline TN...\n")
    
    # 1. Load trained model
    model_path = Path('models/trained/flood_classifier.pkl')
    if not model_path.exists():
        raise FileNotFoundError(
            "❌ Model not found. Run models/train.py first.\n"
            f"   Expected: {model_path}"
        )
    
    model = joblib.load(model_path)
    print("✅ Loaded trained model")
    
    # 2. Load and prepare data
    data_path = Path('data/mock/tn_flood_data.csv')
    if not data_path.exists():
        raise FileNotFoundError(
            "❌ Mock data not found. Run scripts/generate_mock_data.py first.\n"
            f"   Expected: {data_path}"
        )
    
    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df):,} records from {len(df['district'].unique())} districts")
    
    # Engineer features
    df_eng, feature_cols = engineer_features(df, fit_scaler=False)
    X = df_eng[feature_cols]
    
    # Sample 1000 rows for SHAP training (full dataset too slow)
    X_sample = X.sample(n=min(1000, len(X)), random_state=42)
    
    print(f"📊 Using {len(X_sample)} samples for SHAP background")
    print(f"📊 Features: {len(feature_cols)}")
    
    # 3. Create TreeExplainer
    # For VotingClassifier, we need to extract the base estimators
    # Use XGBoost as it's the primary model (60% weight)
    try:
        xgb_model = model.named_estimators_['xgb']
        print("🌳 Extracted XGBoost model (60% ensemble weight)")
    except (AttributeError, KeyError):
        # If not a voting classifier, use model directly
        xgb_model = model
        print("🌳 Using model directly (non-ensemble)")
    
    print("🔬 Creating SHAP TreeExplainer...")
    
    # Import SHAP
    try:
        import shap
    except ImportError:
        raise ImportError(
            "❌ SHAP not installed. Install with:\n"
            "   pip install shap"
        )
    
    explainer = shap.TreeExplainer(xgb_model, X_sample)
    print("✅ SHAP TreeExplainer created")
    
    # 4. Save explainer
    explainer_path = Path('models/trained/shap_explainer.pkl')
    explainer_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(explainer, explainer_path)
    print(f"✅ SHAP explainer saved to {explainer_path}")
    
    # 5. Save feature names for reference
    feature_metadata = {
        "feature_names": feature_cols,
        "num_features": len(feature_cols),
        "feature_display_names": {
            "rainfall_mm": "Daily Rainfall (mm)",
            "river_level_m": "River Level (m above danger)",
            "soil_moisture": "Soil Moisture Index",
            "humidity_pct": "Humidity (%)",
            "reservoir_pct": "Reservoir Capacity (%)",
            "rainfall_7d": "7-Day Cumulative Rainfall (mm)",
            "elevation_m": "Elevation (m)",
            "river_level_3d_avg": "3-Day Avg River Level (m)",
            "rainfall_3d_avg": "3-Day Avg Rainfall (mm)",
            "rainfall_x_soil": "Rainfall × Soil Interaction",
            "river_x_elevation": "River/Elevation Ratio",
            "humidity_x_soil": "Humidity × Soil Interaction",
            "rainfall_lag1": "Yesterday's Rainfall (mm)",
            "river_level_lag1": "Yesterday's River Level (m)",
            "is_monsoon": "Monsoon Season Flag",
            "month_sin": "Month (Sine)",
            "month_cos": "Month (Cosine)",
            "rainfall_7d_intensity": "7-Day Rainfall Intensity",
            "reservoir_overflow_risk": "Reservoir Overflow Risk"
        },
        "created_on": datetime.now().isoformat()
    }
    
    metadata_path = Path('models/trained/shap_feature_names.json')
    with open(metadata_path, 'w') as f:
        json.dump(feature_metadata, f, indent=2)
    
    print(f"✅ Feature metadata saved to {metadata_path}")
    
    return explainer, X_sample, feature_cols


def compute_shap_values(explainer, X, feature_cols, output_class=2):
    """
    Compute SHAP values for given data
    
    Args:
        explainer: Trained SHAP explainer
        X: Feature data (DataFrame or array)
        feature_cols: List of feature names
        output_class: Which class to explain (0=Low, 1=Medium, 2=High)
    
    Returns:
        numpy.ndarray: SHAP values array
    """
    class_names = ['Low', 'Medium', 'High']
    print(f"\n🔬 Computing SHAP values for class '{class_names[output_class]}'...")
    
    shap_values = explainer.shap_values(X)
    
    # For multi-class, shap_values is a list [class_0, class_1, class_2]
    if isinstance(shap_values, list):
        shap_values = shap_values[output_class]
    
    print(f"✅ SHAP values computed (shape: {shap_values.shape})")
    
    return shap_values


def generate_global_summary(explainer, X_sample, feature_cols):
    """
    Generate global SHAP summary plot showing feature importance
    
    Args:
        explainer: SHAP explainer
        X_sample: Sample data for background
        feature_cols: Feature names
    
    Returns:
        Path: Path to saved plot
    """
    print("\n📊 Generating global summary plot...")
    
    import shap
    
    shap_values = explainer.shap_values(X_sample)
    
    # For multi-class, use the High risk class (index 2)
    if isinstance(shap_values, list):
        shap_values_high = shap_values[2]
    else:
        shap_values_high = shap_values
    
    # Create summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values_high, 
        X_sample, 
        feature_names=feature_cols,
        show=False,
        max_display=15
    )
    plt.title("SHAP Feature Importance - High Flood Risk", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save plot
    plot_path = Path('models/shap/global_summary.png')
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Global summary saved to {plot_path}")
    
    return plot_path


def generate_waterfall_chart(explainer, X_instance, feature_cols, expected_value, base64_encode=True):
    """
    Generate waterfall chart for a single prediction
    
    Args:
        explainer: SHAP explainer
        X_instance: Single row DataFrame
        feature_cols: Feature names
        expected_value: Model's base prediction value
        base64_encode: If True, return base64 string instead of saving file
    
    Returns:
        str or Path: Base64 encoded PNG string or file path
    """
    import shap
    
    shap_values = explainer.shap_values(X_instance)
    
    # Handle multi-class output (XGBoost returns 3D array for multi-class)
    if isinstance(shap_values, list):
        # List of arrays, one per class
        shap_values_high = shap_values[2][0]  # High risk class, first sample
        expected = expected_value[2] if isinstance(expected_value, (list, np.ndarray)) else expected_value
    elif len(shap_values.shape) == 3:
        # 3D array (n_samples, n_features, n_classes) - XGBoost multi-class
        shap_values_high = shap_values[0, :, 2]  # First sample, all features, high risk class
        expected = expected_value[2] if isinstance(expected_value, (list, np.ndarray)) else expected_value
    elif len(shap_values.shape) == 2:
        # 2D array (n_samples, n_features) - binary classification
        shap_values_high = shap_values[0]  # First sample
        expected = expected_value if np.isscalar(expected_value) else expected_value[0]
    else:
        # 1D array (n_features) - single sample
        shap_values_high = shap_values
        expected = expected_value
    
    # Create waterfall plot
    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values_high,
            base_values=expected,
            data=X_instance.values[0],
            feature_names=feature_cols
        ),
        show=False
    )
    plt.tight_layout()
    
    if base64_encode:
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        return img_base64
    else:
        # Save to file
        chart_path = Path('models/shap/waterfall_example.png')
        chart_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Example waterfall saved to {chart_path}")
        return chart_path


def precompute_district_explanations():
    """
    Pre-compute SHAP explanations for all districts with high risk predictions
    
    Returns:
        dict: District explanations
    """
    print("\n🗂️ Pre-computing district-level explanations...")
    
    # Load model and explainer
    model = joblib.load('models/trained/flood_classifier.pkl')
    explainer = joblib.load('models/trained/shap_explainer.pkl')
    
    # Load feature names
    with open('models/trained/shap_feature_names.json') as f:
        feature_metadata = json.load(f)
    feature_cols = list(feature_metadata['feature_names'])  # Convert to list for indexing
    display_names = feature_metadata['feature_display_names']
    
    # Load recent flood data (last 30 days of mock data)
    df = pd.read_csv('data/mock/tn_flood_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df_recent = df.sort_values('date').groupby('district').tail(30)
    
    print(f"   Analyzing {len(df_recent):,} recent records from {df_recent['district'].nunique()} districts")
    
    # Engineer features
    df_recent_eng, _ = engineer_features(df_recent, fit_scaler=False)
    X_recent = df_recent_eng[feature_cols]
    
    # Get predictions
    predictions = model.predict_proba(X_recent)
    high_risk_prob = predictions[:, 2] * 100  # Class 2 = High risk
    
    # Filter for high-risk instances (>65% probability)
    high_risk_mask = high_risk_prob > 65
    X_high_risk = X_recent[high_risk_mask]
    districts_high_risk = df_recent[high_risk_mask]['district'].values
    high_risk_probs = high_risk_prob[high_risk_mask]
    
    print(f"   Found {len(X_high_risk)} high-risk predictions (>65% probability)")
    
    if len(X_high_risk) == 0:
        print("   ⚠️  No high-risk predictions found. Lowering threshold to 50%...")
        high_risk_mask = high_risk_prob > 50
        X_high_risk = X_recent[high_risk_mask]
        districts_high_risk = df_recent[high_risk_mask]['district'].values
        high_risk_probs = high_risk_prob[high_risk_mask]
        print(f"   Found {len(X_high_risk)} predictions with >50% risk")
    
    # Compute SHAP values
    try:
        xgb_model = model.named_estimators_['xgb']
    except (AttributeError, KeyError):
        xgb_model = model
    
    shap_values = explainer.shap_values(X_high_risk)
    
    if isinstance(shap_values, list):
        shap_values_high = shap_values[2]  # High risk class
    else:
        shap_values_high = shap_values
    
    # Create explanations for each district
    explanations = {}
    
    for idx, (district, prob) in enumerate(zip(districts_high_risk, high_risk_probs)):
        if district not in explanations:  # Take first occurrence per district
            # Get SHAP values for this instance
            shap_vals = shap_values_high[idx]
            feature_vals = X_high_risk.iloc[idx].values
            
            # Get top 5 features by absolute SHAP value
            abs_shap = np.abs(shap_vals)
            top_indices_array = np.argsort(abs_shap)[-5:][::-1]
            top_indices_list = top_indices_array.tolist()  # Convert to Python list
            
            drivers = []
            for i in top_indices_list:
                feature_name = str(feature_cols[i])  # Ensure string
                shap_val = float(shap_vals[i])
                feature_val = float(feature_vals[i])
                
                # Calculate contribution percentage
                total_impact = np.sum(np.abs(shap_vals))
                contribution_pct = (abs_shap[i] / total_impact) * 100 if total_impact > 0 else 0
                
                drivers.append({
                    "feature": feature_name,
                    "display_name": str(display_names.get(feature_name, feature_name)),
                    "shap_value": round(shap_val, 4),
                    "feature_value": round(feature_val, 2),
                    "contribution_pct": round(contribution_pct, 2),
                    "impact": "increases risk" if shap_val > 0 else "decreases risk"
                })
            
            # Determine risk class
            if prob > 80:
                risk_class = "High"
            elif prob > 65:
                risk_class = "Medium-High"
            else:
                risk_class = "Medium"
            
            explanations[district] = {
                "district": district,
                "flood_probability": round(float(prob), 2),
                "risk_class": risk_class,
                "top_drivers": drivers[:3],  # Top 3 for dashboard
                "all_drivers": drivers,  # All 5 for detailed view
                "explanation_text": f"The primary risk driver for {district} is {display_names.get(drivers[0]['feature'], drivers[0]['feature'])} contributing {drivers[0]['contribution_pct']:.0f}% to the prediction."
            }
    
    # Save explanations
    output_path = Path('models/shap/district_explanations.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(explanations, f, indent=2)
    
    print(f"✅ Saved explanations for {len(explanations)} districts to {output_path}")
    
    return explanations


def main():
    """
    Main execution: Train explainer and generate all SHAP artifacts
    """
    print("=" * 70)
    print("🧠 SHAP EXPLAINABILITY PIPELINE - FLOODLINE TN")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # 1. Train explainer
        print("📋 Step 1: Training SHAP Explainer")
        print("-" * 70)
        explainer, X_sample, feature_cols = train_shap_explainer()
        
        # 2. Generate global summary
        print("\n📋 Step 2: Generating Global Summary Plot")
        print("-" * 70)
        summary_path = generate_global_summary(explainer, X_sample, feature_cols)
        
        # 3. Generate example waterfall chart
        print("\n📋 Step 3: Generating Example Waterfall Chart")
        print("-" * 70)
        print("🌊 Creating waterfall chart for first sample...")
        X_example = X_sample.iloc[[0]]
        expected_value = explainer.expected_value
        waterfall_path = generate_waterfall_chart(
            explainer, X_example, feature_cols, expected_value, base64_encode=False
        )
        
        # 4. Pre-compute district explanations
        print("\n📋 Step 4: Pre-computing District Explanations")
        print("-" * 70)
        explanations = precompute_district_explanations()
        
        # 5. Generate summary report
        print("\n📋 Step 5: Generating Summary Report")
        print("-" * 70)
        
        report = {
            "total_districts_explained": len(explanations),
            "explainer_type": "TreeExplainer (XGBoost)",
            "background_samples": len(X_sample),
            "features_analyzed": len(feature_cols),
            "artifacts_generated": [
                str(summary_path),
                str(waterfall_path),
                "models/shap/district_explanations.json",
                "models/trained/shap_explainer.pkl",
                "models/trained/shap_feature_names.json"
            ],
            "sample_explanation": list(explanations.values())[0] if explanations else None,
            "generated_on": datetime.now().isoformat()
        }
        
        report_path = Path('models/shap/shap_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Summary report saved to {report_path}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("✅ SHAP EXPLAINABILITY PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"   Districts explained: {len(explanations)}")
        print(f"   Features analyzed: {len(feature_cols)}")
        print(f"   Artifacts saved to: models/shap/")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Display sample explanation
        if explanations:
            print("\n📊 Sample Explanation:")
            sample = list(explanations.values())[0]
            print(f"   District: {sample['district']}")
            print(f"   Risk: {sample['risk_class']} ({sample['flood_probability']:.1f}%)")
            print(f"   Top Driver: {sample['top_drivers'][0]['display_name']}")
            print(f"   Contribution: {sample['top_drivers'][0]['contribution_pct']:.1f}%")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ SHAP PIPELINE FAILED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
