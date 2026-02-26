"""
Floodline TN - GeoJSON Report Generator

Generates summary report of GeoJSON files including:
- Feature counts
- Coordinate reference system
- Bounding boxes
- File sizes
- Attribute lists
"""

import json
from pathlib import Path
import sys


def analyze_geojson(file_path):
    """
    Analyze a GeoJSON file and extract metadata
    """
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    
    if not features:
        return None
    
    # Get attributes from first feature
    attributes = list(features[0].get('properties', {}).keys()) if features else []
    
    # Calculate bounding box
    all_coords = []
    for feature in features:
        geom_type = feature.get('geometry', {}).get('type')
        coords = feature.get('geometry', {}).get('coordinates', [])
        
        if geom_type == 'Point':
            all_coords.append(coords)
        elif geom_type == 'Polygon':
            for ring in coords:
                all_coords.extend(ring)
        elif geom_type == 'MultiPolygon':
            for polygon in coords:
                for ring in polygon:
                    all_coords.extend(ring)
    
    if all_coords:
        lons = [c[0] for c in all_coords]
        lats = [c[1] for c in all_coords]
        bounds = [min(lons), min(lats), max(lons), max(lats)]
    else:
        bounds = [0, 0, 0, 0]
    
    # Sample features
    sample_names = []
    for feature in features[:10]:
        name = feature.get('properties', {}).get('district_name') or \
               feature.get('properties', {}).get('taluk_name') or \
               feature.get('properties', {}).get('name', 'Unknown')
        sample_names.append(name)
    
    return {
        "count": len(features),
        "bounds": bounds,
        "attributes": attributes,
        "sample_features": sample_names,
        "file_size_kb": round(file_path.stat().st_size / 1024, 2)
    }


def generate_geojson_report():
    """
    Generate comprehensive GeoJSON report
    """
    print("📊 Generating GeoJSON Report...")
    print()
    
    base_path = Path(__file__).parent.parent / 'data' / 'geospatial'
    
    # Analyze districts
    districts_path = base_path / 'tn_districts.geojson'
    districts_info = analyze_geojson(districts_path)
    
    # Analyze taluks
    taluks_path = base_path / 'tn_taluks.geojson'
    taluks_info = analyze_geojson(taluks_path)
    
    if not districts_info:
        print("❌ Districts GeoJSON not found or invalid")
        return False
    
    # Build report
    report = {
        "generated_at": Path(__file__).parent.parent.name,
        "districts": {
            "file": "tn_districts.geojson",
            "count": districts_info["count"],
            "bounds": {
                "min_lon": districts_info["bounds"][0],
                "min_lat": districts_info["bounds"][1],
                "max_lon": districts_info["bounds"][2],
                "max_lat": districts_info["bounds"][3]
            },
            "center": {
                "lon": round((districts_info["bounds"][0] + districts_info["bounds"][2]) / 2, 4),
                "lat": round((districts_info["bounds"][1] + districts_info["bounds"][3]) / 2, 4)
            },
            "file_size_kb": districts_info["file_size_kb"],
            "attributes": districts_info["attributes"],
            "sample_districts": districts_info["sample_features"]
        }
    }
    
    if taluks_info:
        report["taluks"] = {
            "file": "tn_taluks.geojson",
            "count": taluks_info["count"],
            "file_size_kb": taluks_info["file_size_kb"],
            "attributes": taluks_info["attributes"]
        }
    else:
        report["taluks"] = {
            "status": "not_generated",
            "note": "Taluk boundaries not available"
        }
    
    # Save report
    output_path = base_path / 'geojson_report.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("📊 GeoJSON Report Summary")
    print("=" * 60)
    print()
    print(f"Districts:")
    print(f"  • Count: {report['districts']['count']}")
    print(f"  • File size: {report['districts']['file_size_kb']} KB")
    print(f"  • Center: {report['districts']['center']['lat']}°N, {report['districts']['center']['lon']}°E")
    print(f"  • Attributes: {', '.join(report['districts']['attributes'])}")
    print()
    
    if 'count' in report.get('taluks', {}):
        print(f"Taluks:")
        print(f"  • Count: {report['taluks']['count']}")
        print(f"  • File size: {report['taluks']['file_size_kb']} KB")
        print()
    else:
        print("Taluks: Not generated")
        print()
    
    print(f"Sample Districts:")
    for name in report['districts']['sample_districts'][:5]:
        print(f"  • {name}")
    print()
    
    print("=" * 60)
    print(f"✅ Report saved to: {output_path}")
    print()
    
    return True


def validate_for_leaflet():
    """
    Validate GeoJSON files are ready for Leaflet rendering
    """
    print("🔍 Validating for Leaflet compatibility...")
    print()
    
    districts_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts.geojson'
    
    if not districts_path.exists():
        print("❌ District GeoJSON not found")
        return False
    
    with open(districts_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check structure
    checks = []
    
    checks.append(("FeatureCollection", data.get('type') == 'FeatureCollection'))
    checks.append(("Has features", len(data.get('features', [])) > 0))
    
    if data.get('features'):
        first_feature = data['features'][0]
        checks.append(("Feature type", first_feature.get('type') == 'Feature'))
        checks.append(("Has geometry", 'geometry' in first_feature))
        checks.append(("Has properties", 'properties' in first_feature))
        checks.append(("Has district_id", 'district_id' in first_feature.get('properties', {})))
        checks.append(("Has district_name", 'district_name' in first_feature.get('properties', {})))
    
    print("Validation Results:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ GeoJSON is valid for Leaflet rendering")
    else:
        print("⚠️  Some validation checks failed")
    
    return all_passed


if __name__ == "__main__":
    print("🗺️  Floodline TN - GeoJSON Report Generator")
    print("=" * 60)
    print()
    
    try:
        success = generate_geojson_report()
        
        if success:
            print()
            validate_for_leaflet()
            
            print()
            print("=" * 60)
            print("✅ GeoJSON Report Complete!")
            print()
            print("Next steps:")
            print("  1. Run validation tests: pytest tests/test_geojson.py -v")
            print("  2. Proceed to Module 04: Vulnerability Data")
            print("  3. Or start React dashboard: Module 10")
            sys.exit(0)
        else:
            print("❌ Report generation failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
