import os
import sys
from pathlib import Path

def validate_structure():
    """Validate project directory structure"""
    required_dirs = [
        "data/mock",
        "data/geospatial",
        "data/demographic",
        "data/cache",
        "models/trained",
        "models/metrics",
        "models/shap",
        "pipeline",
        "api/routes",
        "api/middleware",
        "alerts",
        "config",
        "scripts",
        "tests",
        "notebooks"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print("❌ Missing directories:")
        for d in missing:
            print(f"   - {d}")
        return False
    
    print("✅ All required directories present")
    return True

def validate_dependencies():
    """Check critical imports"""
    try:
        import sklearn
        import xgboost
        import fastapi
        import geopandas
        import pandas
        import shap
        print("✅ All critical dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def validate_config():
    """Check config files"""
    required_files = [
        "config/config.yaml",
        "config/districts.json",
        ".env.example",
        "requirements.txt"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing config files:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print("✅ All config files present")
    return True

if __name__ == "__main__":
    print("🔍 Validating Floodline TN project setup...\n")
    
    checks = [
        validate_structure(),
        validate_dependencies(),
        validate_config()
    ]
    
    if all(checks):
        print("\n🎉 Project setup complete! Ready for development.")
        sys.exit(0)
    else:
        print("\n⚠️ Setup incomplete. Fix errors above.")
        sys.exit(1)
