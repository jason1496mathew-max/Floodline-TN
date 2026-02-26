"""
Floodline TN - GeoJSON Processor

Processes raw GeoJSON files:
- Standardizes attributes
- Simplifies geometries
- Adds district metadata
- Generates mock taluk boundaries
"""

import json
from pathlib import Path
import sys

try:
    import geopandas as gpd
    from shapely.geometry import box
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("⚠️  GeoPandas not available. Install with:")
    print("   pip install geopandas")
    print()
    print("Falling back to basic JSON processing...")


def load_district_metadata():
    """Load district metadata from config"""
    config_path = Path(__file__).parent.parent / 'config' / 'districts.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        districts = json.load(f)['districts']
    return {d['name']: d for d in districts}


def process_tn_districts_with_geopandas():
    """
    Process raw GeoJSON using GeoPandas:
    - Filter/validate Tamil Nadu districts
    - Standardize attributes
    - Simplify geometry
    - Convert to EPSG:4326
    """
    print("🔧 Processing TN district boundaries with GeoPandas...")
    
    raw_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts_raw.geojson'
    
    if not raw_path.exists():
        print(f"❌ Raw GeoJSON not found: {raw_path}")
        print("   Run: python scripts/download_geojson.py")
        return None
    
    # Load GeoJSON
    gdf = gpd.read_file(raw_path)
    print(f"✅ Loaded {len(gdf)} features")
    
    # Check CRS (should be EPSG:4326 for web maps)
    if gdf.crs is None:
        print("⚠️  No CRS found, setting to EPSG:4326")
        gdf.set_crs("EPSG:4326", inplace=True)
    elif str(gdf.crs) != "EPSG:4326":
        print(f"Converting from {gdf.crs} to EPSG:4326")
        gdf = gdf.to_crs("EPSG:4326")
    
    print(f"✅ CRS: {gdf.crs}")
    
    # Simplify geometry (reduce file size)
    print("Simplifying geometries...")
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    
    # Load district metadata
    metadata = load_district_metadata()
    
    # Standardize attribute names
    # Try different common field names
    district_col = None
    for col in ['DISTRICT', 'district', 'NAME_2', 'Name', 'name']:
        if col in gdf.columns:
            district_col = col
            break
    
    if district_col:
        gdf.rename(columns={district_col: 'district_name'}, inplace=True)
    else:
        print("⚠️  District name column not found, using index")
        gdf['district_name'] = [f"District_{i+1}" for i in range(len(gdf))]
    
    # Add metadata attributes
    def get_metadata(district_name, field, default=None):
        return metadata.get(district_name, {}).get(field, default)
    
    gdf['district_id'] = gdf['district_name'].apply(lambda x: get_metadata(x, 'id', 0))
    gdf['name_tamil'] = gdf['district_name'].apply(lambda x: get_metadata(x, 'name_tamil', ''))
    gdf['elevation_m'] = gdf['district_name'].apply(lambda x: get_metadata(x, 'elevation_m', 0))
    gdf['lat'] = gdf['district_name'].apply(lambda x: get_metadata(x, 'lat', 0))
    gdf['lon'] = gdf['district_name'].apply(lambda x: get_metadata(x, 'lon', 0))
    
    # Keep only necessary columns
    columns_to_keep = ['district_id', 'district_name', 'name_tamil', 'elevation_m', 'lat', 'lon', 'geometry']
    gdf = gdf[[col for col in columns_to_keep if col in gdf.columns]]
    
    # Remove rows with missing district_id (unmatched districts)
    initial_count = len(gdf)
    gdf = gdf[gdf['district_id'] != 0]
    removed = initial_count - len(gdf)
    if removed > 0:
        print(f"⚠️  Removed {removed} unmatched districts")
    
    # Save processed GeoJSON
    output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts.geojson'
    gdf.to_file(output_path, driver='GeoJSON')
    
    file_size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Processed {len(gdf)} districts")
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size_kb:.1f} KB")
    print()
    
    return gdf


def generate_taluk_mock_with_geopandas(districts_gdf):
    """
    Generate mock taluk boundaries by subdividing districts
    Real taluk data requires detailed shapefiles - use simplified approach for hackathon
    """
    print("🔧 Generating mock taluk boundaries...")
    
    taluks = []
    taluk_id = 1
    
    for idx, row in districts_gdf.iterrows():
        district_name = row['district_name']
        district_geom = row['geometry']
        district_id = row['district_id']
        
        # Get district bounds
        minx, miny, maxx, maxy = district_geom.bounds
        
        # Subdivide into 4 quadrants (simplified taluks)
        midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
        
        quadrants = [
            ('North', minx, midy, maxx, maxy),
            ('South', minx, miny, maxx, midy),
            ('East', midx, miny, maxx, maxy),
            ('West', minx, miny, midx, maxy)
        ]
        
        for direction, x1, y1, x2, y2 in quadrants:
            taluk_geom = district_geom.intersection(box(x1, y1, x2, y2))
            
            if not taluk_geom.is_empty and taluk_geom.area > 0.001:  # Skip tiny fragments
                taluks.append({
                    'taluk_id': taluk_id,
                    'taluk_name': f"{district_name} {direction}",
                    'district_name': district_name,
                    'district_id': district_id,
                    'geometry': taluk_geom
                })
                taluk_id += 1
    
    taluks_gdf = gpd.GeoDataFrame(taluks, crs="EPSG:4326")
    
    output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_taluks.geojson'
    taluks_gdf.to_file(output_path, driver='GeoJSON')
    
    file_size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Generated {len(taluks_gdf)} mock taluks")
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size_kb:.1f} KB")
    print()
    
    return taluks_gdf


def process_without_geopandas():
    """
    Fallback: Basic JSON processing without GeoPandas
    Creates simplified district GeoJSON from metadata
    """
    print("🔧 Processing without GeoPandas (basic mode)...")
    print("⚠️  This will create simplified point-based districts")
    print()
    
    metadata = load_district_metadata()
    
    # Create simple Point geometries from lat/lon
    features = []
    
    for district_name, data in metadata.items():
        feature = {
            "type": "Feature",
            "properties": {
                "district_id": data['id'],
                "district_name": data['name'],
                "name_tamil": data['name_tamil'],
                "elevation_m": data['elevation_m'],
                "lat": data['lat'],
                "lon": data['lon']
            },
            "geometry": {
                "type": "Point",
                "coordinates": [data['lon'], data['lat']]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'geospatial' / 'tn_districts.geojson'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    file_size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Created {len(features)} district points")
    print(f"✅ Saved to: {output_path}")
    print(f"✅ File size: {file_size_kb:.1f} KB")
    print()
    print("⚠️  Note: Using point geometries instead of polygons")
    print("   For full polygon support, install GeoPandas:")
    print("   pip install geopandas")
    print()
    
    # Don't create taluks in basic mode
    print("⚠️  Taluk generation skipped (requires GeoPandas)")
    
    return geojson


if __name__ == "__main__":
    print("🗺️  Floodline TN - GeoJSON Processor")
    print("=" * 60)
    print()
    
    try:
        if GEOPANDAS_AVAILABLE:
            # Full processing with GeoPandas
            districts_gdf = process_tn_districts_with_geopandas()
            
            if districts_gdf is not None and len(districts_gdf) > 0:
                taluks_gdf = generate_taluk_mock_with_geopandas(districts_gdf)
                
                print("=" * 60)
                print("✅ GeoJSON Processing Complete!")
                print()
                print("Generated files:")
                print("  • data/geospatial/tn_districts.geojson")
                print("  • data/geospatial/tn_taluks.geojson")
                print()
                print("Next step: Generate report")
                print("   python scripts/geojson_report.py")
                sys.exit(0)
            else:
                print("❌ District processing failed")
                sys.exit(1)
        else:
            # Fallback processing
            result = process_without_geopandas()
            
            if result:
                print("=" * 60)
                print("✅ Basic GeoJSON Processing Complete!")
                print()
                print("Generated files:")
                print("  • data/geospatial/tn_districts.geojson (points only)")
                print()
                print("For full polygon support, install GeoPandas:")
                print("   pip install geopandas")
                sys.exit(0)
            else:
                print("❌ Processing failed")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
