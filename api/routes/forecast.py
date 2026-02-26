"""
Forecast Routes for Floodline TN API
=====================================

Endpoints for 72-hour rolling forecast with climate scenarios.

Endpoints:
    GET /api/v1/forecast/72h/{district_name} - Get 72-hour forecast
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/forecast/72h/{district_name}")
async def get_72h_forecast(
    district_name: str, 
    scenario: str = Query("normal", regex="^(normal|intensified)$")
):
    """
    Get 72-hour rolling forecast for a district
    
    Args:
        district_name: Name of district
        scenario: 'normal' or 'intensified' (+15% rainfall for climate change scenario)
    
    Returns:
        72-hour forecast with hourly risk probabilities
    
    Example:
        GET /api/v1/forecast/72h/Madurai?scenario=intensified
        
        Response:
        ```json
        {
            "district": "Madurai",
            "scenario": "intensified",
            "forecast_hours": 72,
            "forecast": [
                {
                    "hour": 0,
                    "risk_probability": 65.3,
                    "risk_level": "Medium",
                    "expected_rainfall_mm": 95.2
                }
            ],
            "peak_risk": {
                "hour": 18,
                "probability": 87.5
            }
        }
        ```
    """
    try:
        # Mock forecast data generation
        # In production, this would call weather API and run prediction model
        
        np.random.seed(hash(district_name) % 2**32)  # Consistent for same district
        
        base_time = datetime.now()
        forecast_data = []
        
        # Generate 72 hourly predictions (every 6 hours for compact response)
        for hour in range(0, 73, 6):
            # Mock rainfall pattern (higher in first 24h, tapering off)
            if hour < 24:
                base_rainfall = np.random.uniform(60, 140)
            elif hour < 48:
                base_rainfall = np.random.uniform(30, 80)
            else:
                base_rainfall = np.random.uniform(15, 50)
            
            # Apply scenario multiplier
            if scenario == "intensified":
                base_rainfall *= 1.15
            
            # Mock risk calculation
            # Risk is higher with more rainfall, but adds some variation
            risk_score = min(100, base_rainfall * 0.65 + np.random.uniform(5, 25))
            
            # Calculate confidence interval (wider for longer forecasts)
            uncertainty = 5 + (hour / 72 * 15)  # 5-20% uncertainty
            confidence_lower = max(0, risk_score - uncertainty)
            confidence_upper = min(100, risk_score + uncertainty)
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "High"
            elif risk_score >= 65:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Mock river level (correlated with rainfall)
            river_level = base_rainfall * 0.015 + np.random.uniform(-0.3, 0.3)
            
            forecast_data.append({
                "hour": hour,
                "timestamp": (base_time + timedelta(hours=hour)).isoformat(),
                "risk_probability": round(risk_score, 1),
                "risk_level": risk_level,
                "confidence_lower": round(confidence_lower, 1),
                "confidence_upper": round(confidence_upper, 1),
                "expected_rainfall_mm": round(base_rainfall, 1),
                "expected_river_level_m": round(river_level, 2)
            })
        
        # Find peak risk
        peak_entry = max(forecast_data, key=lambda x: x['risk_probability'])
        
        return {
            "district": district_name,
            "scenario": scenario,
            "scenario_description": {
                "normal": "Current weather patterns",
                "intensified": "Climate change scenario (+15% rainfall)"
            }[scenario],
            "forecast_start": base_time.isoformat(),
            "forecast_hours": 72,
            "data_points": len(forecast_data),
            "forecast": forecast_data,
            "peak_risk": {
                "hour": peak_entry['hour'],
                "timestamp": peak_entry['timestamp'],
                "probability": peak_entry['risk_probability'],
                "expected_rainfall": peak_entry['expected_rainfall_mm']
            },
            "summary": f"Peak flood risk of {peak_entry['risk_probability']:.1f}% expected at hour {peak_entry['hour']} "
                      f"with {peak_entry['expected_rainfall_mm']:.1f}mm rainfall."
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecast generation failed: {str(e)}"
        )


@router.get("/forecast/summary/{district_name}")
async def get_forecast_summary(district_name: str):
    """
    Get simplified 24-hour forecast summary
    
    Args:
        district_name: Name of district
    
    Returns:
        Condensed 24-hour forecast
    """
    try:
        # Get full forecast
        full_forecast = await get_72h_forecast(district_name, "normal")
        
        # Filter to 24 hours
        forecast_24h = [f for f in full_forecast['forecast'] if f['hour'] <= 24]
        
        # Calculate summary stats
        avg_risk = sum(f['risk_probability'] for f in forecast_24h) / len(forecast_24h)
        max_risk = max(f['risk_probability'] for f in forecast_24h)
        total_rainfall = sum(f['expected_rainfall_mm'] for f in forecast_24h)
        
        return {
            "district": district_name,
            "period": "24 hours",
            "average_risk": round(avg_risk, 1),
            "maximum_risk": round(max_risk, 1),
            "total_expected_rainfall_mm": round(total_rainfall, 1),
            "alert_level": "High" if max_risk >= 80 else "Medium" if max_risk >= 65 else "Low",
            "recommendation": "Immediate action required" if max_risk >= 80 
                            else "Monitor situation closely" if max_risk >= 65 
                            else "Stay informed"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecast summary failed: {str(e)}"
        )
