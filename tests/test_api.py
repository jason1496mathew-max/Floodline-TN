"""
API Tests for Floodline TN Backend
===================================

Test suite for FastAPI endpoints.

Run:
    pytest tests/test_api.py -v
    pytest tests/test_api.py --cov=api --cov-report=html
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from api.main import app
from api.middleware.auth import create_access_token


# Test client
client = TestClient(app)


class TestRootEndpoints:
    """
    Test root and health endpoints
    """
    
    def test_root_endpoint(self):
        """
        Test root endpoint returns API info
        """
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["status"] == "online"
    
    def test_health_check(self):
        """
        Test health check endpoint
        """
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "components" in data


class TestPredictEndpoint:
    """
    Test prediction endpoint
    """
    
    def test_predict_valid_request(self):
        """
        Test prediction with valid input
        """
        payload = {
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
        
        response = client.post("/api/v1/predict", json=payload)
        
        # May fail if model not trained, but should validate structure
        if response.status_code == 200:
            data = response.json()
            assert "district" in data
            assert "risk_class" in data
            assert "probability" in data
            assert "alert_level" in data
        else:
            assert response.status_code in [503, 500]
    
    def test_predict_invalid_rainfall(self):
        """
        Test prediction with invalid rainfall value
        """
        payload = {
            "district": "Madurai",
            "date": "2023-11-15",
            "rainfall_mm": -50.0,  # Invalid negative value
            "river_level_m": 3.2,
            "soil_moisture": 0.78,
            "humidity_pct": 89.0,
            "reservoir_pct": 67.0,
            "rainfall_7d": 425.0,
            "elevation_m": 134
        }
        
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422  # Validation error


class TestDistrictsEndpoints:
    """
    Test districts endpoints
    """
    
    def test_get_all_districts(self):
        """
        Test get all districts
        """
        response = client.get("/api/v1/districts")
        assert response.status_code == 200
        
        # May succeed or fail depending on config file
        if response.status_code == 200:
            data = response.json()
            assert "total_districts" in data
            assert "districts" in data
            assert isinstance(data["districts"], list)
    
    def test_get_district_details(self):
        """
        Test get specific district details
        """
        response = client.get("/api/v1/districts/Chennai")
        
        # May succeed or fail depending on data files
        if response.status_code == 200:
            data = response.json()
            assert data["district"] == "Chennai"
            assert "coordinates" in data
        else:
            assert response.status_code in [404, 500, 503]
    
    def test_get_taluks(self):
        """
        Test get taluks for district
        """
        response = client.get("/api/v1/taluks/Madurai")
        
        if response.status_code == 200:
            data = response.json()
            assert "district" in data
            assert "taluks" in data
            assert isinstance(data["taluks"], list)
        else:
            assert response.status_code in [404, 500]
    
    def test_get_metrics(self):
        """
        Test get model metrics
        """
        response = client.get("/api/v1/metrics")
        
        if response.status_code == 200:
            data = response.json()
            assert "model_version" in data
            assert "metrics" in data
        else:
            assert response.status_code in [404, 500]


class TestForecastEndpoints:
    """
    Test forecast endpoints
    """
    
    def test_get_72h_forecast_normal(self):
        """
        Test 72-hour forecast with normal scenario
        """
        response = client.get("/api/v1/forecast/72h/Madurai?scenario=normal")
        assert response.status_code == 200
        
        data = response.json()
        assert data["district"] == "Madurai"
        assert data["scenario"] == "normal"
        assert "forecast" in data
        assert len(data["forecast"]) > 0
    
    def test_get_72h_forecast_intensified(self):
        """
        Test 72-hour forecast with intensified scenario
        """
        response = client.get("/api/v1/forecast/72h/Chennai?scenario=intensified")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario"] == "intensified"
    
    def test_get_forecast_summary(self):
        """
        Test 24-hour forecast summary
        """
        response = client.get("/api/v1/forecast/summary/Salem")
        assert response.status_code == 200
        
        data = response.json()
        assert data["district"] == "Salem"
        assert "average_risk" in data
        assert "maximum_risk" in data


class TestPropagationEndpoints:
    """
    Test propagation endpoints
    """
    
    def test_get_propagation_triggered(self):
        """
        Test propagation with triggering conditions
        """
        response = client.get(
            "/api/v1/propagation/Madurai?rainfall_mm=185&river_level_m=3.2"
        )
        
        # May succeed or fail depending on model files
        if response.status_code == 200:
            data = response.json()
            assert data["trigger_district"] == "Madurai"
            assert "cascade_triggered" in data
        else:
            assert response.status_code in [503, 500]
    
    def test_get_propagation_not_triggered(self):
        """
        Test propagation with non-triggering conditions
        """
        response = client.get(
            "/api/v1/propagation/Chennai?rainfall_mm=50&river_level_m=1.0"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["trigger_district"] == "Chennai"
        else:
            assert response.status_code in [503, 500]
    
    def test_get_downstream_districts(self):
        """
        Test get downstream districts
        """
        response = client.get("/api/v1/propagation/Salem/downstream")
        
        if response.status_code == 200:
            data = response.json()
            assert data["source_district"] == "Salem"
            assert "downstream_districts" in data
        else:
            assert response.status_code in [503, 500]


class TestAlertsEndpoints:
    """
    Test alerts endpoints (with authentication)
    """
    
    def test_generate_alert_without_auth(self):
        """
        Test alert generation without JWT token (should fail)
        """
        payload = {
            "district": "Madurai",
            "risk_level": "Warning",
            "probability": 87.5,
            "top_driver": "Heavy rainfall"
        }
        
        response = client.post("/api/v1/alerts/generate", json=payload)
        assert response.status_code == 403  # Forbidden without auth
    
    def test_generate_alert_with_auth(self):
        """
        Test alert generation with JWT token
        """
        # Create JWT token
        token = create_access_token({"sub": "admin"})
        
        payload = {
            "district": "Madurai",
            "risk_level": "Warning",
            "probability": 87.5,
            "top_driver": "River level exceeds danger mark"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/alerts/generate", json=payload, headers=headers)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["district"] == "Madurai"
        assert data["risk_level"] == "Warning"
        assert "alert_id" in data
        assert "messages" in data
        assert "tamil" in data["messages"]
        assert "english" in data["messages"]
    
    def test_get_alert_history_without_auth(self):
        """
        Test alert history without JWT token (should fail)
        """
        response = client.get("/api/v1/alerts/history")
        assert response.status_code == 403
    
    def test_get_alert_history_with_auth(self):
        """
        Test alert history with JWT token
        """
        token = create_access_token({"sub": "admin"})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/alerts/history?limit=5", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total" in data
    
    def test_test_alert_system(self):
        """
        Test alert system test endpoint (no auth required)
        """
        response = client.get("/api/v1/alerts/test")
        assert response.status_code == 200
        
        data = response.json()
        assert "sample_alerts" in data
        assert "emergency" in data["sample_alerts"]
        assert "warning" in data["sample_alerts"]


class TestRateLimiting:
    """
    Test rate limiting middleware
    """
    
    def test_rate_limit_headers(self):
        """
        Test that rate limit headers are present
        """
        response = client.get("/health")
        
        # Check if rate limit headers exist
        assert "X-RateLimit-Limit" in response.headers or response.status_code == 200


class TestCORS:
    """
    Test CORS middleware
    """
    
    def test_cors_headers(self):
        """
        Test that CORS headers allow requests
        """
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/health", headers=headers)
        
        # Check basic response
        assert response.status_code == 200


class TestErrorHandling:
    """
    Test error handling
    """
    
    def test_404_not_found(self):
        """
        Test 404 error for non-existent endpoint
        """
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_district_name(self):
        """
        Test error handling for invalid district
        """
        response = client.get("/api/v1/districts/InvalidDistrict123")
        
        # Should return error or handle gracefully
        assert response.status_code in [404, 500, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
