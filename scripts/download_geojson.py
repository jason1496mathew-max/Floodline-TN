"""
Floodline TN - GeoJSON Downloader

Downloads Tamil Nadu district boundaries from DataMeet or GADM.
Falls back to mock generation if downloads fail.
"""

import requests
import json
from pathlib import Path
import sys

def download_tn_districts():
    """
    Download Tamil Nadu district boundaries from DataMeet
    """
    print("📥 Downloading TN district GeoJSON from DataMeet...")
    
    # DataMeet Tamil Nadu districts URL
    url = "https://raw.githubusercontent.com/datameet/maps/master/States/Tamil%20Nadu.geojson"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        geojson_data = response.json()
        
        # Save raw download
        output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts_raw.geojson'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
        feature_count = len(geojson_data.get('features', []))
        file_size_kb = output_path.stat().st_size / 1024
        
        print(f"✅ Downloaded {feature_count} features")
        print(f"✅ Saved to: {output_path}")
        print(f"✅ File size: {file_size_kb:.1f} KB")
        
        return output_path
        
    except requests.RequestException as e:
        print(f"❌ DataMeet download failed: {e}")
        print()
        return download_gadm_fallback()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def download_gadm_fallback():
    """
    Fallback: Instructions for manual GADM download
    """
    print("⚠️  Fallback: GADM Manual Download Required")
    print("=" * 60)
    print()
    print("DataMeet download failed. Please download manually:")
    print()
    print("Option 1 - GADM (Recommended):")
    print("   1. Visit: https://gadm.org/download_country.html")
    print("   2. Select Country: India")
    print("   3. Select Level: Level 2 (Districts)")
    print("   4. Select Format: GeoJSON")
    print("   5. Download and extract")
    print("   6. Copy 'gadm41_IND_2.json' to:")
    print(f"      data/geospatial/tn_districts_raw.geojson")
    print()
    print("Option 2 - Use Mock Generator:")
    print("   python scripts/generate_mock_geojson.py")
    print()
    print("After manual download, re-run:")
    print("   python scripts/process_geojson.py")
    print()
    
    return None


def download_india_states():
    """
    Alternative: Download all India states, then filter TN
    """
    print("📥 Attempting alternative: All India states...")
    
    url = "https://raw.githubusercontent.com/datameet/maps/master/Country/india-states.geojson"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        geojson_data = response.json()
        
        # Filter for Tamil Nadu
        tn_features = [
            f for f in geojson_data.get('features', [])
            if f.get('properties', {}).get('ST_NM') == 'Tamil Nadu'
        ]
        
        if tn_features:
            print(f"✅ Found {len(tn_features)} Tamil Nadu features")
            
            output = {
                "type": "FeatureCollection",
                "features": tn_features
            }
            
            output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_state_boundary.geojson'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved state boundary to: {output_path}")
            print("⚠️  Note: This is state-level, not district-level")
            print("   Run mock generator for districts: python scripts/generate_mock_geojson.py")
            
            return output_path
        else:
            print("❌ Tamil Nadu not found in data")
            return None
            
    except Exception as e:
        print(f"❌ Alternative download failed: {e}")
        return None


def verify_download():
    """
    Verify if GeoJSON file exists and is valid
    """
    raw_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts_raw.geojson'
    
    if not raw_path.exists():
        return False
    
    try:
        with open(raw_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('type') != 'FeatureCollection':
            print("⚠️  Warning: Not a FeatureCollection")
            return False
        
        feature_count = len(data.get('features', []))
        if feature_count == 0:
            print("⚠️  Warning: No features found")
            return False
        
        print(f"✅ Verified: {feature_count} features found")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("🗺️  Floodline TN - GeoJSON Downloader")
    print("=" * 60)
    print()
    
    # Try main download
    result = download_tn_districts()
    
    # If failed, try alternative
    if result is None:
        print()
        print("Trying alternative source...")
        result = download_india_states()
    
    print()
    print("=" * 60)
    
    # Verify
    if result:
        if verify_download():
            print("✅ Download successful!")
            print()
            print("Next step: Process GeoJSON")
            print("   python scripts/process_geojson.py")
            sys.exit(0)
        else:
            print("⚠️  Download verification failed")
            sys.exit(1)
    else:
        print("❌ All download attempts failed")
        print()
        print("Recommended: Use mock GeoJSON generator")
        print("   python scripts/generate_mock_geojson.py")
        sys.exit(1)
