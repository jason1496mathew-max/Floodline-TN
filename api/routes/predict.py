"""
Prediction Routes for Floodline TN API
=======================================

Endpoints for flood risk prediction using ML models.

Endpoints:
    POST /api/v1/predict - Single district prediction with SHAP explanation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from models.predict import FloodPredictor
from models.shap_helpers import generate_live_shap_explanation


router = APIRouter()


# Request model
class PredictRequest(BaseModel):
    """
    Request model for flood prediction
    """
    district: str = Field(..., example="Madurai", description="District name")
    date: str = Field(..., example="2023-11-15", description="Date in YYYY-MM-DD format")
    rainfall_mm: float = Field(..., ge=0, le=500, example=185.0, description="Rainfall in mm")
    river_level_m: float = Field(..., ge=-2, le=5, example=3.2, description="River level above danger mark (m)")
    soil_moisture: float = Field(..., ge=0, le=1, example=0.78, description="Soil moisture (0-1)")
    humidity_pct: float = Field(..., ge=0, le=100, example=89.0, description="Humidity percentage")
    reservoir_pct: float = Field(..., ge=0, le=100, example=67.0, description="Reservoir level percentage")
    rainfall_7d: float = Field(..., ge=0, example=425.0, description="7-day cumulative rainfall (mm)")
    elevation_m: float = Field(..., ge=0, example=134, description="District elevation (m)")
    
    class Config:
        schema_extra = {
            "example": {
                "district": "Madurai",
                "date": "2023-11-15",
                "rainfall_mm": 185.0,
                "river_level_m": 3.2,
                "soil_moisture": 0.78,
                "humidity_pct": 89.0,
                "reservoir_pct": 67.0,
                "rainfall_7d": 425.0,
                "elevation_m": 134
            }
        }


# Response model
class PredictResponse(BaseModel):
    """
    Response model for flood prediction
    """
    district: str
    date: str
    risk_class: str
    probability: float
    probabilities: Dict[str, float]
    shap_drivers: Optional[Dict] = None
    alert_level: str
    recommendation: str
    timestamp: str


# Initialize predictor (singleton pattern)
predictor = None


def get_predictor():
    """
    Get or initialize predictor instance
    
    Returns:
        FloodPredictor instance
    
    Raises:
        HTTPException: If model files not found
    """
    global predictor
    if predictor is None:
        try:
            predictor = FloodPredictor()
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=503,
                detail="ML model not available. Please train the model first using: python models/train.py"
            )
    return predictor


@router.post("/predict", response_model=PredictResponse)
async def predict_flood_risk(request: PredictRequest):
    """
    Predict flood risk for a single district with given parameters
    
    Returns:
        Prediction with risk class, probability, and SHAP explanation
    
    Example:
        ```json
        POST /api/v1/predict
        {
            "district": "Madurai",
            "rainfall_mm": 185.0,
            "river_level_m": 3.2,
            ...
        }
        ```
    
    Response:
        ```json
        {
            "district": "Madurai",
            "risk_class": "High",
            "probability": 87.23,
            "alert_level": "Warning",
            "shap_drivers": {...}
        }
        ```
    """
    try:
        # Prepare input data
        input_data = pd.DataFrame([{
            'date': request.date,
            'district': request.district,
            'rainfall_mm': request.rainfall_mm,
            'river_level_m': request.river_level_m,
            'soil_moisture': request.soil_moisture,
            'humidity_pct': request.humidity_pct,
            'reservoir_pct': request.reservoir_pct,
            'rainfall_7d': request.rainfall_7d,
            'elevation_m': request.elevation_m
        }])
        
        # Get prediction
        pred = get_predictor()
        result = pred.predict(input_data)
        
        # Generate SHAP explanation
        try:
            shap_explanation = generate_live_shap_explanation(input_data)
        except Exception as e:
            print(f"⚠️ SHAP generation failed: {e}")
            shap_explanation = None
        
        # Determine alert level based on probability
        prob = result['probability']
        if prob >= 85:
            alert_level = "Emergency"
            recommendation = "Immediate evacuation required. Move to higher ground now."
        elif prob >= 65:
            alert_level = "Warning"
            recommendation = "High risk of flooding. Prepare for evacuation."
        elif prob >= 50:
            alert_level = "Watch"
            recommendation = "Moderate risk. Monitor weather updates closely."
        else:
            alert_level = "Advisory"
            recommendation = "Low risk. Stay informed about weather conditions."
        
        return PredictResponse(
            district=request.district,
            date=request.date,
            risk_class=result['risk_class'],
            probability=round(result['probability'], 2),
            probabilities={
                str(k): round(float(v), 2) 
                for k, v in result['probabilities'].items()
            },
            shap_drivers=shap_explanation,
            alert_level=alert_level,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
