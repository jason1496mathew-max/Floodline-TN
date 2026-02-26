"""
Generate district risk predictions for demo
"""

import json
import numpy as np
from pathlib import Path

# Load districts
with open('config/districts.json', 'r', encoding='utf-8') as f:
    districts_config = json.load(f)['districts']

# Load vulnerability scores to base risk on
import pandas as pd
vuln_df = pd.read_csv('data/demographic/vulnerability_index.csv')
vuln_dict = dict(zip(vuln_df['district_name'], vuln_df['vulnerability_index']))

# Generate predictions 
explanations = {}

for district in districts_config:
    name = district['name']
    vuln_score = vuln_dict.get(name, 50.0)
    
    # Convert vulnerability (0-100) to flood probability (0-1)
    # Add some randomness
    base_prob = vuln_score / 100.0
    flood_probability = min(max(base_prob + np.random.normal(0, 0.1), 0.0), 1.0)
    
    # Determine risk class
    if flood_probability >= 0.75:
        risk_class = "High"
    elif flood_probability >= 0.50:
        risk_class = "Medium"
    else:
        risk_class = "Low"
    
    # Generate mock top drivers
    drivers = [
        {
            "feature": "rainfall_x_soil",
            "display_name": "Rainfall × Soil Interaction",
            "shap_value": round(flood_probability * 0.3, 4),
            "feature_value": round(np.random.uniform(50, 150), 2),
            "contribution_pct": 35.0,
            "impact": "increases risk"
        },
        {
            "feature": "humidity_x_soil",
            "display_name": "Humidity × Soil Interaction",
            "shap_value": round(flood_probability * 0.25, 4),
            "feature_value": round(np.random.uniform(0.6, 0.9), 2),
            "contribution_pct": 28.0,
            "impact": "increases risk"
        },
        {
            "feature": "rainfall_mm",
            "display_name": "Daily Rainfall",
            "shap_value": round(flood_probability * 0.2, 4),
            "feature_value": round(np.random.uniform(20, 120), 2),
            "contribution_pct": 22.0,
            "impact": "increases risk"
        }
    ]
    
    explanation_text = f"{name} shows {risk_class.lower()} flood risk due to elevated rainfall-soil interaction and high soil moisture levels."
    
    explanations[name] = {
        "district": name,
        "flood_probability": round(flood_probability, 2),
        "risk_class": risk_class,
        "top_drivers": drivers,
        "explanation_text": explanation_text
    }

# Save explanations
output_path = Path('models/shap/district_explanations.json')
output_path.parent.mkdir(exist_ok=True, parents=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(explanations, f, indent=2, ensure_ascii=False)

print(f"✅ Generated predictions for {len(explanations)} districts")
print(f"✅ Saved to {output_path}")

# Show sample
print("\n📊 Sample predictions:")
for name, exp in list(explanations.items())[:5]:
    print(f"   {name}: {exp['risk_class']} ({exp['flood_probability']*100:.1f}%)")
