"""
Propagation Routes for Floodline TN API
========================================

Endpoints for river flood propagation timeline and cascade modeling.

Endpoints:
    GET /api/v1/propagation/{trigger_district} - Get cascade timeline
    GET /api/v1/propagation/{trigger_district}/downstream - Get downstream districts
"""

from fastapi import APIRouter, HTTPException, Query
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from models.propagation_api import PropagationAPI


router = APIRouter()


# Initialize propagation model (singleton)
prop_api = None


def get_propagation_api():
    """
    Get or initialize propagation API instance
    
    Returns:
        PropagationAPI instance
    
    Raises:
        HTTPException: If propagation model not available
    """
    global prop_api
    if prop_api is None:
        try:
            prop_api = PropagationAPI()
            if not prop_api.initialized:
                raise Exception("Propagation model failed to initialize")
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Propagation model not available: {str(e)}"
            )
    return prop_api


@router.get("/propagation/{trigger_district}")
async def get_river_propagation(
    trigger_district: str,
    rainfall_mm: float = Query(150.0, ge=0, le=500, description="Current rainfall in mm"),
    river_level_m: float = Query(2.5, ge=-2, le=5, description="River level above danger mark in m")
):
    """
    Get river flood propagation timeline for a trigger district
    
    Args:
        trigger_district: Upstream district name (e.g., "Madurai")
        rainfall_mm: Current rainfall (for trigger evaluation)
        river_level_m: River level above danger mark
    
    Returns:
        Cascade scenario with timeline of downstream flood events
    
    Example:
        GET /api/v1/propagation/Madurai?rainfall_mm=185&river_level_m=3.2
        
        Response:
        ```json
        {
            "trigger_district": "Madurai",
            "cascade_triggered": true,
            "affected_districts": 3,
            "max_propagation_hours": 21.5,
            "timeline": [
                {
                    "district": "Madurai",
                    "onset_hour": 0,
                    "risk_level": "Critical"
                },
                {
                    "district": "Sivaganga",
                    "onset_hour": 12,
                    "risk_level": "High"
                }
            ]
        }
        ```
    """
    try:
        api = get_propagation_api()
        
        # Get cascade prediction
        scenario = api.get_cascade_prediction(
            district=trigger_district,
            rainfall_mm=rainfall_mm,
            river_level_m=river_level_m
        )
        
        if not scenario or not scenario.get('triggered'):
            return {
                "trigger_district": trigger_district,
                "cascade_triggered": False,
                "reason": scenario.get('reason', 'Conditions below trigger thresholds'),
                "current_conditions": {
                    "rainfall_mm": rainfall_mm,
                    "river_level_m": river_level_m
                },
                "trigger_thresholds": {
                    "rainfall_mm": 150.0,
                    "river_level_m": 2.5
                }
            }
        
        return {
            "trigger_district": scenario['trigger_district'],
            "cascade_triggered": True,
            "trigger_reason": scenario['trigger_reason'],
            "affected_districts": scenario['affected_districts_count'],
            "max_propagation_hours": scenario['max_propagation_hours'],
            "rivers_involved": scenario.get('rivers_involved', []),
            "timeline": scenario['timeline'],
            "evacuation_priority": scenario.get('evacuation_priority', []),
            "summary": scenario['summary'],
            "trigger_conditions": scenario.get('trigger_conditions', {}),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Propagation calculation failed: {str(e)}"
        )


@router.get("/propagation/{trigger_district}/downstream")
async def get_downstream_districts(trigger_district: str):
    """
    Get list of all districts downstream from trigger point
    
    Args:
        trigger_district: Source district name
    
    Returns:
        List of downstream districts requiring alerts
    
    Example:
        GET /api/v1/propagation/Salem/downstream
        
        Response:
        ```json
        {
            "source_district": "Salem",
            "downstream_districts": ["Erode", "Karur", "Tiruchirappalli", "Thanjavur", "Nagapattinam"],
            "downstream_count": 5,
            "alert_required": true,
            "rivers": ["Cauvery"]
        }
        ```
    """
    try:
        api = get_propagation_api()
        result = api.get_downstream_alerts(trigger_district)
        
        return {
            "source_district": result['source_district'],
            "downstream_districts": result['downstream_districts'],
            "downstream_count": result['downstream_count'],
            "alert_required": result['alert_required'],
            "rivers": result.get('rivers', []),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Downstream lookup failed: {str(e)}"
        )


@router.get("/propagation/district-info/{district_name}")
async def get_district_propagation_info(district_name: str):
    """
    Get district information for propagation modeling
    
    Args:
        district_name: District name
    
    Returns:
        District metadata for propagation calculations
    """
    try:
        api = get_propagation_api()
        info = api.get_district_info(district_name)
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"District '{district_name}' not found in river network"
            )
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"District info lookup failed: {str(e)}"
        )
