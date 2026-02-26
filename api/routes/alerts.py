"""
Alerts Routes for Floodline TN API
===================================

JWT-protected endpoints for alert generation and history.

Endpoints:
    POST /api/v1/alerts/generate - Generate multi-channel alert (protected)
    GET /api/v1/alerts/history - Get alert history (protected)
    POST /api/v1/alerts/test - Test alert system (no auth)
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.middleware.auth import verify_token
from alerts.alert_engine import AlertEngine
from alerts.sms_mock import SMSDispatcher
from alerts.translations import get_district_tamil_name


router = APIRouter()
security = HTTPBearer()

# Initialize alert engine and SMS dispatcher
alert_engine = AlertEngine()
sms_dispatcher = SMSDispatcher()


# Alert request model
class AlertRequest(BaseModel):
    """
    Request model for alert generation
    """
    district: str = Field(..., example="Madurai")
    probability: float = Field(..., ge=0, le=100)
    top_driver: str = Field(..., example="Heavy rainfall in upstream region")
    driver_contribution: float = Field(default=40.0, ge=0, le=100)
    additional_context: Optional[Dict] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "district": "Madurai",
                "probability": 87.5,
                "top_driver": "Vaigai river level exceeds danger mark",
                "driver_contribution": 42.3,
                "additional_context": {
                    "rainfall_mm": 185.0,
                    "river_level_m": 3.2
                }
            }
        }


@router.post("/alerts/generate")
async def generate_alert(
    request: AlertRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate multi-channel alert using AlertEngine - JWT protected
    
    Requires JWT authentication token in Authorization header.
    
    Args:
        request: Alert request with district and risk info
        credentials: JWT credentials
    
    Returns:
        Alert generation result with message previews and dispatch status
    
    Example:
        ```
        POST /api/v1/alerts/generate
        Authorization: Bearer <jwt_token>
        
        {
            "district": "Madurai",
            "probability": 87.5,
            "top_driver": "River level exceeds danger mark",
            "driver_contribution": 42.3
        }
        ```
    """
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials)
        
        # Get district Tamil name
        district_tamil = get_district_tamil_name(request.district)
        
        # Generate alert using AlertEngine
        alert = alert_engine.generate_alert(
            district=request.district,
            district_tamil=district_tamil,
            flood_probability=request.probability,
            top_driver={
                "display_name": request.top_driver,
                "contribution_pct": request.driver_contribution
            },
            additional_context=request.additional_context
        )
        
        if alert.get('status') == 'no_alert':
            return alert
        
        # Validate alert
        if not alert_engine.validate_alert(alert):
            raise HTTPException(
                status_code=500,
                detail="Generated alert failed validation"
            )
        
        # Dispatch SMS for Warning/Emergency levels
        if alert['alert_level'] in ['Warning', 'Emergency']:
            dispatch_result = sms_dispatcher.dispatch_sms(
                alert,
                recipients="all" if alert['alert_level'] == 'Emergency' else "officials"
            )
            alert['sms_dispatch'] = dispatch_result
        
        # Add user info
        alert['generated_by'] = payload.get("sub", "system")
        
        return alert
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alert generation failed: {str(e)}"
        )


@router.get("/alerts/history")
async def get_alert_history(
    limit: int = 10,
    district: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get alert history - JWT protected
    
    Retrieves SMS dispatch history from SMSDispatcher logs.
    
    Args:
        limit: Maximum number of alerts to return (default: 10)
        district: Optional filter by district
        credentials: JWT credentials
    
    Returns:
        List of recent alerts with dispatch information
    
    Example:
        ```
        GET /api/v1/alerts/history?limit=5&district=Madurai
        Authorization: Bearer <jwt_token>
        ```
    """
    try:
        # Verify JWT token
        verify_token(credentials.credentials)
        
        # Get dispatch history from SMS dispatcher
        history = sms_dispatcher.get_dispatch_history(limit=limit, district=district)
        
        # Get dispatch statistics
        stats = sms_dispatcher.get_dispatch_stats()
        
        return {
            "total": len(history),
            "alerts": history,
            "statistics": stats,
            "query": {
                "limit": limit,
                "district_filter": district
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alert history: {str(e)}"
        )


@router.post("/alerts/test")
async def test_alert_system():
    """
    Test alert system without authentication (for demo purposes)
    
    Generates sample alerts for all 4 severity levels.
    
    Returns:
        Sample alert messages in Tamil and English for all levels
    """
    from alerts.alert_engine import AlertLevel
    from alerts.translations import get_action_text
    
    test_districts = [
        ("Chennai", "சென்னை", 55),
        ("Salem", "சேலம்", 70),
        ("Madurai", "மதுரை", 85),
        ("Coimbatore", "கோயம்புத்தூர்", 95)
    ]
    
    sample_alerts = {}
    
    for district_en, district_ta, probability in test_districts:
        alert = alert_engine.generate_alert(
            district=district_en,
            district_tamil=district_ta,
            flood_probability=probability,
            top_driver={
                "display_name": "Test scenario driver",
                "contribution_pct": 40.0
            }
        )
        
        if alert.get('status') != 'no_alert':
            level = alert['alert_level'].lower()
            sample_alerts[level] = {
                "district": district_en,
                "district_tamil": district_ta,
                "probability": probability,
                "tamil": alert['messages']['tamil'],
                "english": alert['messages']['english'],
                "sms_tamil": alert['messages']['sms_tamil'],
                "sms_english": alert['messages']['sms_english'],
                "channels": alert['channels'],
                "dashboard_format": alert_engine.format_for_dashboard(alert)
            }
    
    return {
        "status": "test",
        "sample_alerts": sample_alerts,
        "alert_levels": {
            "advisory": "50-64% probability",
            "watch": "65-79% probability",
            "warning": "80-89% probability",
            "emergency": "90-100% probability"
        },
        "system_info": {
            "version": "1.0.0",
            "engine": "AlertEngine with SHAP integration",
            "languages": ["Tamil", "English"]
        }
    }


@router.get("/alerts/dashboard/{district}")
async def get_dashboard_alert(district: str):
    """
    Get current active alert for district in dashboard format (no auth for demo)
    
    Args:
        district: District name
    
    Returns:
        Dashboard-formatted alert or null if no active alert
    """
    try:
        # Check recent history for this district
        history = sms_dispatcher.get_dispatch_history(limit=5, district=district)
        
        if not history:
            return {
                "district": district,
                "active_alert": None,
                "message": "No active alerts"
            }
        
        # Get most recent alert
        latest = history[-1]
        
        # Mock reconstruction of alert for dashboard
        # In production, fetch from database
        return {
            "district": district,
            "active_alert": {
                "alert_id": latest['alert_id'],
                "level": latest['alert_level'],
                "probability": latest.get('alert_metadata', {}).get('probability', 0),
                "color": {
                    "Advisory": "#2196F3",
                    "Watch": "#FFC107",
                    "Warning": "#FF9800",
                    "Emergency": "#F44336"
                }.get(latest['alert_level'], "#2196F3"),
                "icon": {
                    "Advisory": "ℹ️",
                    "Watch": "⚠️",
                    "Warning": "🚨",
                    "Emergency": "🔴"
                }.get(latest['alert_level'], "⚠️"),
                "timestamp": latest['dispatched_at'],
                "top_driver": latest.get('alert_metadata', {}).get('top_driver', 'N/A')
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard alert: {str(e)}"
        )

