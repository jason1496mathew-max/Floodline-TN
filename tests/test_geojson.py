"""
Test suite for GeoJSON validation

Validates:
- File existence
- GeoJSON structure
- Coordinate reference system
- Required attributes
- Geometry validity
- Feature counts
- Leaflet compatibility
"""

import json
import pytest
from pathlib import Path

# Paths to GeoJSON files
DATA_PATH = Path(__file__).parent.parent / 'data' / 'geospatial'
DISTRICTS_PATH = DATA_PATH / 'tn_districts.geojson'
TALUKS_PATH = DATA_PATH / 'tn_taluks.geojson'
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'districts.json'


class TestGeoJSONExistence:
    """Test if GeoJSON files exist"""
    
    def test_districts_geojson_exists(self):
        """Check if processed districts GeoJSON exists"""
        assert DISTRICTS_PATH.exists(), f"Districts GeoJSON not found at {DISTRICTS_PATH}"
    
    def test_districts_is_valid_json(self):
        """Check if districts file is valid JSON"""
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data is not None, "Districts file is not valid JSON"
    
    def test_taluks_geojson_exists(self):
        """Check if taluks GeoJSON exists"""
        # Taluks are optional for MVP
        if TALUKS_PATH.exists():
            with open(TALUKS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert data is not None, "Taluks file is not valid JSON"


class TestGeoJSONStructure:
    """Test GeoJSON structure and format"""
    
    @pytest.fixture
    def districts_data(self):
        """Load districts GeoJSON"""
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_is_feature_collection(self, districts_data):
        """Validate it's a FeatureCollection"""
        assert districts_data.get('type') == 'FeatureCollection', \
            "GeoJSON must be a FeatureCollection"
    
    def test_has_features(self, districts_data):
        """Check features array exists and has content"""
        features = districts_data.get('features', [])
        assert len(features) > 0, "FeatureCollection has no features"
    
    def test_feature_structure(self, districts_data):
        """Validate feature structure"""
        features = districts_data.get('features', [])
        
        for i, feature in enumerate(features[:5]):  # Check first 5
            assert feature.get('type') == 'Feature', f"Feature {i} type must be 'Feature'"
            assert 'geometry' in feature, f"Feature {i} missing geometry"
            assert 'properties' in feature, f"Feature {i} missing properties"
    
    def test_geometry_types(self, districts_data):
        """Validate geometry types are supported"""
        valid_types = ['Point', 'Polygon', 'MultiPolygon', 'LineString']
        features = districts_data.get('features', [])
        
        for i, feature in enumerate(features):
            geom_type = feature.get('geometry', {}).get('type')
            assert geom_type in valid_types, \
                f"Feature {i} has unsupported geometry type: {geom_type}"


class TestGeoJSONAttributes:
    """Test required attributes"""
    
    @pytest.fixture
    def districts_data(self):
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_required_attributes(self, districts_data):
        """Validate required attributes are present"""
        required_attrs = ['district_id', 'district_name']
        features = districts_data.get('features', [])
        
        for i, feature in enumerate(features):
            props = feature.get('properties', {})
            for attr in required_attrs:
                assert attr in props, \
                    f"Feature {i} missing required attribute: {attr}"
    
    def test_district_id_unique(self, districts_data):
        """Check district IDs are unique"""
        features = districts_data.get('features', [])
        district_ids = [f.get('properties', {}).get('district_id') for f in features]
        
        # Remove None values
        district_ids = [id for id in district_ids if id is not None]
        
        assert len(district_ids) == len(set(district_ids)), \
            "District IDs are not unique"
    
    def test_district_names_not_empty(self, districts_data):
        """Check district names are not empty"""
        features = districts_data.get('features', [])
        
        for i, feature in enumerate(features):
            name = feature.get('properties', {}).get('district_name', '')
            assert len(name) > 0, f"Feature {i} has empty district_name"


class TestGeoJSONCounts:
    """Test feature counts"""
    
    @pytest.fixture
    def districts_data(self):
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def config_districts(self):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)['districts']
    
    def test_minimum_districts(self, districts_data):
        """Check minimum number of districts"""
        features = districts_data.get('features', [])
        assert len(features) >= 5, f"Expected at least 5 districts, got {len(features)}"
    
    def test_matches_config(self, districts_data, config_districts):
        """Check district count roughly matches config"""
        features = districts_data.get('features', [])
        config_count = len(config_districts)
        
        # Allow some tolerance for unmatched districts
        assert len(features) >= config_count * 0.5, \
            f"GeoJSON has {len(features)} districts, config has {config_count}"


class TestGeoJSONCoordinates:
    """Test coordinate validity"""
    
    @pytest.fixture
    def districts_data(self):
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_coordinates_in_india_bounds(self, districts_data):
        """Validate coordinates are within India/Tamil Nadu bounds"""
        # Tamil Nadu bounds: approximately
        # Lat: 8.0 to 13.5
        # Lon: 76.0 to 80.5
        
        features = districts_data.get('features', [])
        
        for feature in features:
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [])
            
            if geom.get('type') == 'Point':
                lon, lat = coords
                assert 75 <= lon <= 81, f"Longitude {lon} out of TN bounds"
                assert 7 <= lat <= 14, f"Latitude {lat} out of TN bounds"
            
            elif geom.get('type') == 'Polygon':
                for ring in coords:
                    for lon, lat in ring:
                        assert 75 <= lon <= 81, f"Longitude {lon} out of TN bounds"
                        assert 7 <= lat <= 14, f"Latitude {lat} out of TN bounds"


class TestLeafletCompatibility:
    """Test Leaflet map compatibility"""
    
    @pytest.fixture
    def districts_data(self):
        with open(DISTRICTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_is_wgs84_compatible(self, districts_data):
        """Coordinates should be in WGS84 (EPSG:4326) format"""
        # Check that coordinates are in decimal degrees
        features = districts_data.get('features', [])
        
        if features:
            first_geom = features[0].get('geometry', {})
            coords = first_geom.get('coordinates', [])
            
            # For polygon, get first coordinate
            if first_geom.get('type') == 'Polygon':
                if coords and coords[0]:
                    lon, lat = coords[0][0]
                    # Check reasonable decimal degree range
                    assert -180 <= lon <= 180, "Longitude not in decimal degrees"
                    assert -90 <= lat <= 90, "Latitude not in decimal degrees"
    
    def test_file_size_reasonable(self, districts_data):
        """File should be optimized for web (<1MB for districts)"""
        file_size_kb = DISTRICTS_PATH.stat().st_size / 1024
        
        # Allow up to 1MB for districts
        assert file_size_kb < 1024, \
            f"Districts file too large: {file_size_kb:.1f} KB (max 1024 KB)"
    
    def test_properties_json_serializable(self, districts_data):
        """All properties should be JSON serializable"""
        features = districts_data.get('features', [])
        
        for feature in features:
            props = feature.get('properties', {})
            # Try to serialize
            try:
                json.dumps(props)
            except (TypeError, ValueError) as e:
                pytest.fail(f"Properties not JSON serializable: {e}")


class TestTaluksOptional:
    """Test taluks if they exist"""
    
    def test_taluks_structure(self):
        """If taluks exist, validate structure"""
        if not TALUKS_PATH.exists():
            pytest.skip("Taluks GeoJSON not generated")
        
        with open(TALUKS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data.get('type') == 'FeatureCollection'
        features = data.get('features', [])
        assert len(features) > 0, "Taluks FeatureCollection has no features"
        
        # Check first feature structure
        if features:
            first = features[0]
            props = first.get('properties', {})
            assert 'taluk_id' in props or 'taluk_name' in props, \
                "Taluk missing required identifiers"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
