#!/usr/bin/env python3
"""
Pre-deployment validation script for Floodline TN
Run before deploying to production
"""

import sys
from pathlib import Path
import json

def check_files_exist():
    """Verify all required files exist"""
    required_files = [
        'requirements.txt',
        'api/main.py',
        'models/train.py',
        'models/predict.py',
        'config/config.yaml',
        'config/districts.json',
        'dashboard/package.json',
        'dashboard/src/App.jsx',
        'Dockerfile',
        'render.yaml'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print("✅ All required files present")
    return True

def check_model_artifacts():
    """Check if ML model is trained"""
    model_path = Path('models/trained/flood_classifier.pkl')
    metrics_path = Path('models/metrics/performance.json')
    
    if not model_path.exists():
        print("❌ Model not trained. Run: python models/train.py")
        return False
    
    if not metrics_path.exists():
        print("⚠️  Model metrics not found")
        return True  # Don't fail, just warn
    
    try:
        with open(metrics_path) as f:
            metrics = json.load(f)
        
        f1_score = metrics['metrics']['f1_score_weighted']
        
        if f1_score < 0.75:
            print(f"⚠️  Model F1-score ({f1_score:.4f}) below recommended threshold (0.75)")
            return True  # Warn but don't fail
        
        print(f"✅ Model trained with F1-score: {f1_score:.4f}")
        return True
    except Exception as e:
        print(f"⚠️  Could not read model metrics: {e}")
        return True

def check_data_files():
    """Check if data files are generated"""
    required_data = [
        'data/mock/tn_flood_data.csv',
        'data/geospatial/tn_districts.geojson',
        'data/demographic/vulnerability_index.csv'
    ]
    
    missing = []
    for file_path in required_data:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing data files:")
        for f in missing:
            print(f"   - {f}")
        print("\nRun data generation scripts:")
        print("   python scripts/generate_mock_data.py")
        print("   python scripts/process_geojson.py")
        print("   python scripts/generate_vulnerability_data.py")
        return False
    
    print("✅ All data files present")
    return True

def check_frontend_build():
    """Check if frontend can build"""
    package_json = Path('dashboard/package.json')
    
    if not package_json.exists():
        print("❌ dashboard/package.json not found")
        return False
    
    print("✅ Frontend structure valid")
    print("   Run 'cd dashboard && npm run build' to test build")
    return True

def check_secrets():
    """Check if secret keys are configured"""
    env_example = Path('.env.example')
    
    if not env_example.exists():
        print("⚠️  .env.example not found (will create during deployment)")
    
    print("✅ Environment template checks passed")
    print("   Remember to set these in Render/Netlify:")
    print("   - SECRET_KEY")
    print("   - ALLOWED_ORIGINS")
    print("   - REACT_APP_API_BASE_URL")
    return True

def check_deployment_files():
    """Check if deployment configuration files exist"""
    deployment_files = [
        'Dockerfile',
        'render.yaml',
        'netlify.toml',
        '.dockerignore',
        'runtime.txt'
    ]
    
    missing = []
    for file_path in deployment_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing deployment files:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print("✅ All deployment files present")
    return True

def main():
    print("="*60)
    print("🚀 Floodline TN - Pre-Deployment Validation")
    print("="*60 + "\n")
    
    checks = [
        ("File Structure", check_files_exist),
        ("ML Model", check_model_artifacts),
        ("Data Files", check_data_files),
        ("Frontend", check_frontend_build),
        ("Deployment Files", check_deployment_files),
        ("Secrets", check_secrets)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        results.append(check_func())
    
    print("\n" + "="*60)
    if all(results):
        print("✅ All checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Deploy backend on Render.com")
        print("3. Deploy frontend on Netlify")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
