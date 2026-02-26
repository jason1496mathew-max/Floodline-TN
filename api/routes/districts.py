"""
Districts Routes for Floodline TN API
======================================

Endpoints for district risk data and SHAP explanations.

Endpoints:
    GET /api/v1/districts - List all districts with current risk
    GET /api/v1/districts/{district_name} - Get district details with SHAP
    GET /api/v1/taluks/{district_name} - Get taluk-level risk breakdown
    GET /api/v1/metrics - Get ML model performance metrics
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import pandas as pd
import json
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from models.shap_helpers import get_shap_explanation


router = APIRouter()


@router.get("/districts")
async def get_all_districts():
    """
    Get list of all districts with current risk levels
    
    Returns:
        List of all Tamil Nadu districts with risk scores
    
    Example Response:
        ```json
        {
            "total_districts": 21,
            "districts": [{
                "district_id": 1,
                "name": "Chennai",
                "name_tamil": "சென்னை",
                "risk_probability": 0.75,
                "risk_class": "High",
                ...
            }],
            "timestamp": "2023-11-15T10:30:00"
        }
        ```
    """
    try:
        # Load pre-computed SHAP explanations (high-risk districts)
        explanations_path = Path('models/shap/district_explanations.json')
        
        if explanations_path.exists():
            with open(explanations_path, 'r', encoding='utf-8') as f:
                explanations = json.load(f)
        else:
            explanations = {}
        
        # Load district metadata
        districts_config_path = Path('config/districts.json')
        if not districts_config_path.exists():
            raise HTTPException(
                status_code=503,
                detail="Districts configuration not found"
            )
        
        with open(districts_config_path, 'r', encoding='utf-8') as f:
            districts_config = json.load(f)['districts']
        
        # Load vulnerability index with demographic details
        vulnerability_path = Path('data/demographic/vulnerability_index.csv')
        vulnerability_data = {}
        vulnerability_df_full = pd.DataFrame()  # Store full dataframe
        if vulnerability_path.exists():
            vuln_df = pd.read_csv(vulnerability_path)
            vulnerability_data = dict(zip(vuln_df['district_name'], vuln_df['vulnerability_index']))
            vulnerability_df_full = vuln_df
        
        # Combine data
        districts_list = []
        for district in districts_config:
            name = district['name']
            explanation = explanations.get(name, None)
            
            # Get risk info from explanation or use default
            if explanation:
                risk_probability = explanation.get('flood_probability', 0.0)
                risk_class = explanation.get('risk_class', 'Low')
            else:
                # Use a default medium risk if no explanation available
                risk_probability = 0.5
                risk_class = "Medium"
            
            # Calculate enhanced evacuation priority using elderly population & healthcare
            vuln_score = vulnerability_data.get(name, 50.0)  # 0-100
            flood_risk_pct = risk_probability * 100  # Convert to percentage
            
            # Get demographic factors for prioritization
            evacuation_priority = 0
            priority_level = 'Low'
            
            if not vulnerability_df_full.empty:
                district_demo = vulnerability_df_full[vulnerability_df_full['district_name'] == name]
                if not district_demo.empty:
                    elderly_pct = district_demo.iloc[0]['elderly_pct']  # % of elderly
                    hospital_count = district_demo.iloc[0]['hospital_count']  # Absolute count
                    population = district_demo.iloc[0]['population']
                    
                    # Healthcare availability per 10k people (lower = higher priority)
                    healthcare_per_10k = (hospital_count / population) * 10000
                    healthcare_priority = 100 - min(healthcare_per_10k * 10, 100)  # Invert and normalize
                    
                    # Weighted evacuation priority formula:
                    # 40% flood risk, 30% elderly population, 20% healthcare scarcity, 10% general vulnerability
                    evacuation_priority = round(
                        (0.40 * flood_risk_pct) + 
                        (0.30 * (elderly_pct * 5)) +  # Scale elderly % to 0-100
                        (0.20 * healthcare_priority) + 
                        (0.10 * vuln_score), 2
                    )
                else:
                    # Fallback to simple formula
                    evacuation_priority = round((0.5 * flood_risk_pct) + (0.5 * vuln_score), 2)
            else:
                # Fallback to simple formula
                evacuation_priority = round((0.5 * flood_risk_pct) + (0.5 * vuln_score), 2)
            
            # Determine priority level
            if evacuation_priority >= 80:
                priority_level = 'Critical'
            elif evacuation_priority >= 60:
                priority_level = 'High'
            elif evacuation_priority >= 40:
                priority_level = 'Medium'
            else:
                priority_level = 'Low'
            
            districts_list.append({
                "district_id": district['id'],
                "name": name,
                "name_tamil": district['name_tamil'],
                "coordinates": {
                    "lat": district['lat'],
                    "lon": district['lon']
                },
                "elevation_m": district['elevation_m'],
                "population": district['population'],
                "major_rivers": district['major_rivers'],
                "vulnerability_score": vulnerability_data.get(name, 50.0) / 100.0,  # Normalize to 0-1
                "risk_probability": round(risk_probability, 2),
                "risk_class": risk_class,
                "evacuation_priority": evacuation_priority,
                "priority_level": priority_level,
                "last_updated": datetime.now().isoformat()
            })
        
        return {
            "total_districts": len(districts_list),
            "districts": districts_list,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve districts: {str(e)}"
        )


@router.get("/districts/{district_name}")
async def get_district_details(district_name: str):
    """
    Get detailed information for a specific district including SHAP explanation
    
    Args:
        district_name: Name of the district
    
    Returns:
        District details with SHAP explanation and risk drivers
    
    Example:
        GET /api/v1/districts/Madurai
        
        Response:
        ```json
        {
            "district": "Madurai",
            "name_tamil": "மதுரை",
            "coordinates": {"lat": 9.9252, "lon": 78.1198},
            "risk": {
                "class": "High",
                "probability": 0.87
            },
            "top_drivers": [
                {"feature": "river_level_m", "contribution": 0.42}
            ]
        }
        ```
    """
    try:
        # Get SHAP explanation
        explanation = get_shap_explanation(district_name)
        
        if not explanation:
            # Try mock fallback
            print(f"⚠️ No SHAP explanation for {district_name}, using fallback")
            explanation = None
        
        # Load district metadata
        with open('config/districts.json', 'r', encoding='utf-8') as f:
            districts_config = json.load(f)['districts']
        
        # Load vulnerability index with demographic details
        vulnerability_path = Path('data/demographic/vulnerability_index.csv')
        vulnerability_data = {}
        vulnerability_df_full = pd.DataFrame()
        if vulnerability_path.exists():
            vuln_df = pd.read_csv(vulnerability_path)
            vulnerability_data = dict(zip(vuln_df['district_name'], vuln_df['vulnerability_index']))
            vulnerability_df_full = vuln_df
        
        district_meta = next((d for d in districts_config if d['name'] == district_name), None)
        
        if not district_meta:
            raise HTTPException(
                status_code=404,
                detail=f"District '{district_name}' not found in configuration"
            )
        
        result = {
            "district": district_name,
            "district_id": district_meta['id'],
            "name_tamil": district_meta['name_tamil'],
            "coordinates": {
                "lat": district_meta['lat'],
                "lon": district_meta['lon']
            },
            "elevation_m": district_meta['elevation_m'],
            "population": district_meta['population'],
            "major_rivers": district_meta['major_rivers'],
            "vulnerability_score": vulnerability_data.get(district_name, 50.0) / 100.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add risk info if explanation available
        if explanation:
            flood_probability = explanation['flood_probability']
            result["risk"] = {
                "class": explanation['risk_class'],
                "probability": flood_probability
            }
            result["top_drivers"] = explanation['top_drivers']
            result["explanation_text"] = explanation['explanation_text']
            
            # Calculate enhanced evacuation priority using elderly population & healthcare
            vuln_score = vulnerability_data.get(district_name, 50.0)
            flood_risk_pct = flood_probability * 100
            
            evacuation_priority = 0
            priority_level = 'Low'
            
            if not vulnerability_df_full.empty:
                district_demo = vulnerability_df_full[vulnerability_df_full['district_name'] == district_name]
                if not district_demo.empty:
                    elderly_pct = district_demo.iloc[0]['elderly_pct']
                    hospital_count = district_demo.iloc[0]['hospital_count']
                    population = district_demo.iloc[0]['population']
                    elderly_population = district_demo.iloc[0]['elderly_population']
                    
                    # Healthcare availability per 10k people (lower = higher priority)
                    healthcare_per_10k = (hospital_count / population) * 10000
                    healthcare_priority = 100 - min(healthcare_per_10k * 10, 100)
                    
                    # Weighted evacuation priority formula:
                    # 40% flood risk, 30% elderly population, 20% healthcare scarcity, 10% general vulnerability
                    evacuation_priority = round(
                        (0.40 * flood_risk_pct) + 
                        (0.30 * (elderly_pct * 5)) +
                        (0.20 * healthcare_priority) + 
                        (0.10 * vuln_score), 2
                    )
                    
                    # Add demographic details to response
                    result["demographics"] = {
                        "elderly_population": int(elderly_population),
                        "elderly_percentage": round(elderly_pct, 1),
                        "hospital_count": int(hospital_count),
                        "hospitals_per_10k": round(healthcare_per_10k, 2)
                    }
                else:
                    evacuation_priority = round((0.5 * flood_risk_pct) + (0.5 * vuln_score), 2)
            else:
                evacuation_priority = round((0.5 * flood_risk_pct) + (0.5 * vuln_score), 2)
            
            if evacuation_priority >= 80:
                priority_level = 'Critical'
            elif evacuation_priority >= 60:
                priority_level = 'High'
            elif evacuation_priority >= 40:
                priority_level = 'Medium'
            else:
                priority_level = 'Low'
            
            result["evacuation_priority"] = evacuation_priority
            result["priority_level"] = priority_level
        else:
            # Use vulnerability score as fallback
            vuln = district_meta['vulnerability_score']
            result["risk"] = {
                "class": "High" if vuln >= 0.75 else "Medium" if vuln >= 0.50 else "Low",
                "probability": vuln
            }
            result["top_drivers"] = []
            result["explanation_text"] = f"{district_name} has moderate flood vulnerability based on geographic and demographic factors."
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve district details: {str(e)}"
        )


@router.get("/taluks/{district_name}")
async def get_taluks(district_name: str):
    """
    Get taluk-level risk breakdown for a district
    
    Args:
        district_name: Name of the district
    
    Returns:
        List of taluks with vulnerability scores
    
    Example:
        GET /api/v1/taluks/Madurai
    """
    try:
        # Load taluk vulnerability data
        taluks_path = Path('data/demographic/taluk_vulnerability.csv')
        
        if not taluks_path.exists():
            # Return mock data for demo
            return {
                "district": district_name,
                "total_taluks": 3,
                "taluks": [
                    {
                        "taluk_id": 1,
                        "taluk_name": f"{district_name} North",
                        "taluk_name_tamil": f"{district_name} வடக்கு",
                        "vulnerability_score": 0.75,
                        "vulnerability_level": "High"
                    },
                    {
                        "taluk_id": 2,
                        "taluk_name": f"{district_name} Central",
                        "taluk_name_tamil": f"{district_name} மத்திய",
                        "vulnerability_score": 0.68,
                        "vulnerability_level": "Medium"
                    },
                    {
                        "taluk_id": 3,
                        "taluk_name": f"{district_name} South",
                        "taluk_name_tamil": f"{district_name} தெற்கு",
                        "vulnerability_score": 0.62,
                        "vulnerability_level": "Medium"
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "note": "Mock data for demonstration"
            }
        
        df = pd.read_csv(taluks_path)
        district_taluks = df[df['district_name'] == district_name]
        
        if district_taluks.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No taluks found for district '{district_name}'"
            )
        
        taluks_list = []
        for _, row in district_taluks.iterrows():
            taluks_list.append({
                "taluk_id": str(row['taluk_id']),  # Keep as string since IDs like "11-S"
                "taluk_name": row['taluk_name'],
                "taluk_name_tamil": row.get('taluk_name_tamil', ''),
                "vulnerability_score": round(float(row['vulnerability_index']), 2),
                "vulnerability_level": row['vulnerability_level']
            })
        
        return {
            "district": district_name,
            "total_taluks": len(taluks_list),
            "taluks": taluks_list,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve taluks: {str(e)}"
        )


@router.get("/metrics")
async def get_model_metrics():
    """
    Get ML model performance metrics
    
    Returns:
        Model training metrics and metadata
    
    Example Response:
        ```json
        {
            "model_version": "1.0.0",
            "trained_on": "2023-11-15T10:30:00",
            "metrics": {
                "f1_score": 0.83,
                "precision": 0.81,
                "recall": 0.85
            }
        }
        ```
    """
    try:
        metrics_path = Path('models/metrics/performance.json')
        
        if not metrics_path.exists():
            # Return mock metrics for demo
            return {
                "model_version": "1.0.0",
                "trained_on": datetime.now().isoformat(),
                "metrics": {
                    "f1_score": 0.83,
                    "precision": 0.81,
                    "recall": 0.85,
                    "accuracy": 0.82,
                    "false_alarm_rate": 0.12
                },
                "cross_validation": {
                    "mean_f1": 0.81,
                    "std_f1": 0.03
                },
                "features_count": 19,
                "note": "Mock metrics for demonstration"
            }
        
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
        
        return {
            "model_version": metrics.get('model_version', '1.0.0'),
            "trained_on": metrics.get('trained_on', datetime.now().isoformat()),
            "metrics": metrics.get('metrics', {}),
            "cross_validation": metrics.get('cross_validation', {}),
            "features_count": len(metrics.get('features', []))
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )
