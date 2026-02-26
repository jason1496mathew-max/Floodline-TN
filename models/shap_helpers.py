"""
SHAP Helper Functions for Floodline TN
=======================================

API-ready helper functions for retrieving and generating SHAP explanations.

Functions:
    - get_shap_explanation(district_name): Retrieve pre-computed explanation
    - generate_live_shap_explanation(input_data): Generate real-time explanation
    - get_all_explanations(): Get all pre-computed explanations
    - get_feature_importance(): Get global feature importance

Usage:
    from models.shap_helpers import get_shap_explanation
    
    explanation = get_shap_explanation("Chennai")
    print(explanation['top_drivers'])
"""

import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional


def get_shap_explanation(district_name: str) -> Optional[Dict]:
    """
    Retrieve pre-computed SHAP explanation for a district
    
    Args:
        district_name: Name of the district (e.g., "Chennai", "Madurai")
    
    Returns:
        Dictionary with SHAP explanation containing:
            - district: District name
            - flood_probability: Risk probability (0-100)
            - risk_class: Risk class (Low/Medium/High)
            - top_drivers: Top 3 feature drivers
            - all_drivers: All 5 feature drivers
            - explanation_text: Human-readable explanation
        Returns None if district not found
    
    Example:
        >>> explanation = get_shap_explanation("Chennai")
        >>> print(explanation['flood_probability'])
        87.5
        >>> print(explanation['top_drivers'][0]['display_name'])
        7-Day Cumulative Rainfall (mm)
    """
    explanations_path = Path('models/shap/district_explanations.json')
    
    if not explanations_path.exists():
        print(f"⚠️  Explanations file not found: {explanations_path}")
        return None
    
    try:
        with open(explanations_path) as f:
            explanations = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error loading explanations JSON: {e}")
        return None
    
    return explanations.get(district_name, None)


def get_all_explanations() -> Dict[str, Dict]:
    """
    Get all pre-computed SHAP explanations
    
    Returns:
        Dictionary mapping district names to their explanations
        Returns empty dict if file not found
    
    Example:
        >>> explanations = get_all_explanations()
        >>> print(f"Explained {len(explanations)} districts")
        >>> for district, exp in explanations.items():
        ...     print(f"{district}: {exp['risk_class']}")
    """
    explanations_path = Path('models/shap/district_explanations.json')
    
    if not explanations_path.exists():
        print(f"⚠️  Explanations file not found: {explanations_path}")
        return {}
    
    try:
        with open(explanations_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error loading explanations JSON: {e}")
        return {}


def generate_live_shap_explanation(input_data: pd.DataFrame, target_class: int = 2) -> Dict:
    """
    Generate SHAP explanation for new input data (real-time)
    
    Args:
        input_data: Single row DataFrame with raw features (before engineering)
        target_class: Which class to explain (0=Low, 1=Medium, 2=High)
    
    Returns:
        Dictionary with SHAP drivers:
            - top_drivers: List of top 3 features with contributions
            - explanation_text: Human-readable explanation
            - target_class: Class being explained
    
    Raises:
        FileNotFoundError: If explainer or feature metadata not found
    
    Example:
        >>> data = pd.DataFrame({
        ...     'date': ['2023-11-15'],
        ...     'district': ['Chennai'],
        ...     'rainfall_mm': [185.0],
        ...     'river_level_m': [3.2],
        ...     'soil_moisture': [0.78],
        ...     'humidity_pct': [89.0],
        ...     'reservoir_pct': [67.0],
        ...     'rainfall_7d': [425.0],
        ...     'elevation_m': [7]
        ... })
        >>> explanation = generate_live_shap_explanation(data)
        >>> print(explanation['explanation_text'])
    """
    from pipeline.feature_engineering import engineer_features
    
    # Check if explainer exists
    explainer_path = Path('models/trained/shap_explainer.pkl')
    if not explainer_path.exists():
        raise FileNotFoundError(
            f"SHAP explainer not found. Run models/shap_explain.py first.\n"
            f"Expected: {explainer_path}"
        )
    
    # Check if feature metadata exists
    metadata_path = Path('models/trained/shap_feature_names.json')
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Feature metadata not found. Run models/shap_explain.py first.\n"
            f"Expected: {metadata_path}"
        )
    
    # Load explainer
    explainer = joblib.load(explainer_path)
    
    # Load feature metadata
    with open(metadata_path) as f:
        metadata = json.load(f)
    feature_cols = metadata['feature_names']
    display_names = metadata['feature_display_names']
    
    # Engineer features
    input_eng, _ = engineer_features(input_data, fit_scaler=False)
    X = input_eng[feature_cols]
    
    # Compute SHAP values
    shap_values = explainer.shap_values(X)
    
    # Extract values for target class
    if isinstance(shap_values, list):
        shap_vals = shap_values[target_class][0]  # Target class, first instance
    else:
        shap_vals = shap_values[0]
    
    # Get top 3 drivers by absolute SHAP value
    abs_shap = np.abs(shap_vals)
    top_indices = np.argsort(abs_shap)[-3:][::-1]
    
    drivers = []
    total_impact = np.sum(abs_shap)
    
    class_names = ['Low', 'Medium', 'High']
    
    for i in top_indices:
        feature = feature_cols[i]
        shap_val = float(shap_vals[i])
        abs_val = abs_shap[i]
        contribution = (abs_val / total_impact * 100) if total_impact > 0 else 0
        
        drivers.append({
            "feature": feature,
            "display_name": display_names.get(feature, feature),
            "contribution_pct": round(contribution, 2),
            "shap_value": round(shap_val, 4),
            "impact": "increases risk" if shap_val > 0 else "decreases risk"
        })
    
    return {
        "top_drivers": drivers,
        "explanation_text": f"{drivers[0]['display_name']}: {drivers[0]['contribution_pct']:.0f}% risk driver",
        "target_class": class_names[target_class],
        "total_features_analyzed": len(feature_cols)
    }


def get_feature_importance(top_n: int = 10) -> List[Dict]:
    """
    Get global feature importance from all pre-computed explanations
    
    Args:
        top_n: Number of top features to return
    
    Returns:
        List of dictionaries with feature names and average importance
        Sorted by importance (descending)
    
    Example:
        >>> importance = get_feature_importance(top_n=5)
        >>> for feat in importance:
        ...     print(f"{feat['display_name']}: {feat['avg_contribution']:.1f}%")
    """
    explanations = get_all_explanations()
    
    if not explanations:
        return []
    
    # Load feature metadata for display names
    metadata_path = Path('models/trained/shap_feature_names.json')
    display_names = {}
    
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
            display_names = metadata.get('feature_display_names', {})
    
    # Aggregate contributions across all districts
    feature_contributions = {}
    
    for district_data in explanations.values():
        for driver in district_data.get('all_drivers', []):
            feature = driver['feature']
            contribution = driver['contribution_pct']
            
            if feature not in feature_contributions:
                feature_contributions[feature] = []
            
            feature_contributions[feature].append(contribution)
    
    # Calculate average contributions
    feature_importance = []
    
    for feature, contributions in feature_contributions.items():
        avg_contribution = np.mean(contributions)
        
        feature_importance.append({
            "feature": feature,
            "display_name": display_names.get(feature, feature),
            "avg_contribution": round(avg_contribution, 2),
            "occurrences": len(contributions)
        })
    
    # Sort by average contribution (descending)
    feature_importance.sort(key=lambda x: x['avg_contribution'], reverse=True)
    
    return feature_importance[:top_n]


def format_explanation_for_display(explanation: Dict, include_all_drivers: bool = False) -> str:
    """
    Format SHAP explanation as human-readable text for display
    
    Args:
        explanation: Explanation dictionary from get_shap_explanation()
        include_all_drivers: If True, include all drivers; else only top 3
    
    Returns:
        Formatted string for display
    
    Example:
        >>> exp = get_shap_explanation("Chennai")
        >>> print(format_explanation_for_display(exp))
    """
    if not explanation:
        return "No explanation available"
    
    district = explanation['district']
    risk_class = explanation['risk_class']
    probability = explanation['flood_probability']
    
    lines = [
        f"🏙️  District: {district}",
        f"⚠️  Risk Level: {risk_class} ({probability:.1f}% probability)",
        "",
        "📊 Risk Drivers:"
    ]
    
    drivers = explanation['all_drivers'] if include_all_drivers else explanation['top_drivers']
    
    for i, driver in enumerate(drivers, 1):
        display_name = driver['display_name']
        contribution = driver['contribution_pct']
        impact = driver['impact']
        
        emoji = "📈" if impact == "increases risk" else "📉"
        lines.append(f"   {i}. {emoji} {display_name}: {contribution:.1f}%")
    
    return "\n".join(lines)


# Test functions
def test_helpers():
    """
    Test all helper functions
    """
    print("🧪 Testing SHAP Helper Functions\n")
    print("=" * 70)
    
    # Test 1: Get all explanations
    print("\n1. Testing get_all_explanations()...")
    explanations = get_all_explanations()
    print(f"   ✅ Found {len(explanations)} district explanations")
    
    if not explanations:
        print("   ⚠️  No explanations found. Run models/shap_explain.py first.")
        return
    
    # Test 2: Get single explanation
    print("\n2. Testing get_shap_explanation()...")
    district_name = list(explanations.keys())[0]
    explanation = get_shap_explanation(district_name)
    
    if explanation:
        print(f"   ✅ Retrieved explanation for {district_name}")
        print(f"   Risk: {explanation['risk_class']} ({explanation['flood_probability']:.1f}%)")
        print(f"   Top Driver: {explanation['top_drivers'][0]['display_name']}")
        print(f"   Contribution: {explanation['top_drivers'][0]['contribution_pct']:.1f}%")
    else:
        print(f"   ❌ Failed to retrieve explanation for {district_name}")
    
    # Test 3: Get feature importance
    print("\n3. Testing get_feature_importance()...")
    importance = get_feature_importance(top_n=5)
    print(f"   ✅ Top 5 Most Important Features:")
    for i, feat in enumerate(importance, 1):
        print(f"      {i}. {feat['display_name']}: {feat['avg_contribution']:.1f}%")
    
    # Test 4: Format explanation
    print("\n4. Testing format_explanation_for_display()...")
    formatted = format_explanation_for_display(explanation, include_all_drivers=False)
    print(f"   ✅ Formatted explanation:\n")
    for line in formatted.split('\n'):
        print(f"      {line}")
    
    print("\n" + "=" * 70)
    print("✅ All helper function tests passed!")


if __name__ == "__main__":
    test_helpers()
