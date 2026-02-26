"""
Floodline TN - Mock GeoJSON Generator

Generates simplified polygon boundaries for Tamil Nadu districts
when real GeoJSON data is unavailable.

Creates approximate district polygons based on centroid coordinates
and estimated sizes.
"""

import json
from pathlib import Path
import math


def load_district_metadata():
    """Load district metadata from config"""
    config_path = Path(__file__).parent.parent / 'config' / 'districts.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        districts = json.load(f)['districts']
    return districts


def create_polygon_around_point(lon, lat, size_degrees=0.5):
    """
    Create a simple square polygon around a point
    
    Args:
        lon: Longitude of center
        lat: Latitude of center
        size_degrees: Size of square in degrees (~55km per 0.5 degrees)
    
    Returns:
        GeoJSON Polygon coordinates
    """
    half_size = size_degrees / 2
    
    # Create square coordinates (clockwise)
    coordinates = [[
        [lon - half_size, lat - half_size],  # SW
        [lon + half_size, lat - half_size],  # SE
        [lon + half_size, lat + half_size],  # NE
        [lon - half_size, lat + half_size],  # NW
        [lon - half_size, lat - half_size]   # Close the ring
    ]]
    
    return coordinates


def create_irregular_polygon(lon, lat, size_degrees=0.5, irregularity=0.2):
    """
    Create a more realistic irregular polygon
    
    Args:
        lon: Longitude of center
        lat: Latitude of center
        size_degrees: Base size
        irregularity: Amount of variation (0-1)
    
    Returns:
        GeoJSON Polygon coordinates
    """
    import math
    
    # Create octagon with variations
    num_points = 8
    points = []
    
    for i in range(num_points + 1):  # +1 to close the ring
        angle = (2 * math.pi * i) / num_points
        
        # Add some irregularity
        radius = size_degrees * (1 + irregularity * math.sin(angle * 3))
        
        x = lon + radius * math.cos(angle)
        y = lat + radius * math.sin(angle)
        
        points.append([x, y])
    
    return [points]


def generate_mock_districts():
    """
    Generate mock district GeoJSON with approximate polygons
    """
    print("🔧 Generating mock district GeoJSON...")
    
    districts = load_district_metadata()
    features = []
    
    for district in districts:
        # Determine size based on elevation (rough proxy for district size)
        # Coastal/low elevation districts tend to be smaller
        base_size = 0.4 if district['elevation_m'] < 50 else 0.5
        
        # Create irregular polygon
        coordinates = create_irregular_polygon(
            district['lon'],
            district['lat'],
            size_degrees=base_size,
            irregularity=0.3
        )
        
        feature = {
            "type": "Feature",
            "properties": {
                "district_id": district['id'],
                "district_name": district['name'],
                "name_tamil": district['name_tamil'],
                "elevation_m": district['elevation_m'],
                "lat": district['lat'],
                "lon": district['lon']
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "Mock generated",
            "description": "Simplified district boundaries for development",
            "note": "Not accurate for production use"
        }
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts.geojson'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    file_size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Generated {len(features)} mock district polygons")
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size_kb:.1f} KB")
    print()
    
    return geojson


def generate_mock_taluks():
    """
    Generate mock taluk GeoJSON (4 taluks per district)
    """
    print("🔧 Generating mock taluk GeoJSON...")
    
    districts = load_district_metadata()
    features = []
    taluk_id = 1
    
    for district in districts:
        # Create 4 taluks per district (quadrants)
        base_size = 0.25
        
        quadrants = [
            ('North', 0, base_size),
            ('South', 0, -base_size),
            ('East', base_size, 0),
            ('West', -base_size, 0)
        ]
        
        for direction, offset_lon, offset_lat in quadrants:
            taluk_lon = district['lon'] + offset_lon
            taluk_lat = district['lat'] + offset_lat
            
            coordinates = create_irregular_polygon(
                taluk_lon,
                taluk_lat,
                size_degrees=0.2,
                irregularity=0.2
            )
            
            feature = {
                "type": "Feature",
                "properties": {
                    "taluk_id": taluk_id,
                    "taluk_name": f"{district['name']} {direction}",
                    "district_name": district['name'],
                    "district_id": district['id']
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
            features.append(feature)
            taluk_id += 1
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "Mock generated",
            "description": "Simplified taluk boundaries for development"
        }
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_taluks.geojson'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    file_size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Generated {len(features)} mock taluks")
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size_kb:.1f} KB")
    print()
    
    return geojson


if __name__ == "__main__":
    print("🗺️  Floodline TN - Mock GeoJSON Generator")
    print("=" * 60)
    print()
    print("⚠️  Generating simplified mock boundaries")
    print("   These are approximate and not accurate for production")
    print()
    
    try:
        districts = generate_mock_districts()
        taluks = generate_mock_taluks()
        
        print("=" * 60)
        print("✅ Mock GeoJSON Generation Complete!")
        print()
        print("Generated files:")
        print("  • data/geospatial/tn_districts.geojson")
        print("  • data/geospatial/tn_taluks.geojson")
        print()
        print("Next step: Generate report")
        print("   python scripts/geojson_report.py")
        print()
        print("Note: For accurate boundaries, use:")
        print("   python scripts/download_geojson.py")
        
    except Exception as e:
        print(f"❌ Error generating mock GeoJSON: {e}")
        import traceback
        traceback.print_exc()
