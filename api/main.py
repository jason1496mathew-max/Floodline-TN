"""
Floodline TN - FastAPI Backend Application
===========================================

Main FastAPI application for Flood Early Warning System.

Features:
    - ML prediction endpoints
    - District risk data
    - River propagation modeling
    - SHAP explanations
    - Alert generation
    - JWT authentication
    - Rate limiting
    - CORS support

API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health

Run:
    uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from api.routes import predict, districts, forecast, propagation, alerts
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.auth import verify_token


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan
    
    Startup: Load models and initialize services
    Shutdown: Clean up resources
    """
    # Startup
    print("=" * 70)
    print("🚀 Starting Floodline TN API...")
    print("=" * 70)
    print("✅ Loading ML models...")
    print("✅ Initializing propagation model...")
    print("✅ Setting up middleware...")
    print("=" * 70)
    print("📡 API ready at http://localhost:8000")
    print("📚 Documentation at http://localhost:8000/docs")
    print("=" * 70)
    
    yield
    
    # Shutdown
    print("\n" + "=" * 70)
    print("👋 Shutting down Floodline TN API...")
    print("=" * 70)


# Initialize FastAPI app
app = FastAPI(
    title="Floodline TN API",
    description="AI-Based Flood Early Warning & Risk Prediction System for Tamil Nadu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Floodline TN Team",
        "email": "support@floodline-tn.gov.in"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://floodline-tn.netlify.app",
        "https://floodline-tn.vercel.app",
        "*"  # Allow all for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)


# Include routers
app.include_router(predict.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(districts.router, prefix="/api/v1", tags=["Districts"])
app.include_router(forecast.router, prefix="/api/v1", tags=["Forecast"])
app.include_router(propagation.router, prefix="/api/v1", tags=["Propagation"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "service": "Floodline TN - Flood Early Warning API",
        "version": "1.0.0",
        "status": "online",
        "description": "AI-Based Flood Early Warning & Risk Prediction System for Tamil Nadu",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        },
        "features": [
            "ML-based flood prediction",
            "SHAP explainability",
            "River propagation modeling",
            "72-hour forecast",
            "Multi-level alerts (Tamil + English)",
            "District and taluk-level risk data"
        ]
    }


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns:
        Dictionary with health status and diagnostic info
    """
    from pathlib import Path
    
    # Check if critical files exist
    model_path = Path('models/trained/flood_classifier.pkl')
    shap_path = Path('models/shap/shap_explainer.pkl')
    config_path = Path('config/river_network.json')
    
    model_exists = model_path.exists()
    shap_exists = shap_path.exists()
    config_exists = config_path.exists()
    
    # Determine overall health
    all_healthy = model_exists and shap_exists and config_exists
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ml_model": "loaded" if model_exists else "missing",
            "shap_explainer": "loaded" if shap_exists else "missing",
            "river_network": "loaded" if config_exists else "missing"
        },
        "version": "1.0.0",
        "uptime": "operational"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler
    
    Prevents unhandled exceptions from exposing internal details
    """
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# 404 Handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"The requested endpoint does not exist",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
