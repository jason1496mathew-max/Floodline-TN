"""
Test Suite for SHAP Explainer Module
=====================================

Tests for SHAP explainer training, helper functions, and artifacts.

Test Classes:
    - TestSHAPArtifacts: File existence checks
    - TestSHAPExplainer: Explainer functionality
    - TestSHAPExplanations: District explanations validation
    - TestSHAPHelpers: Helper function tests
    - TestSHAPVisualization: Plot generation tests

Run:
    pytest tests/test_shap.py -v
    python -m pytest tests/test_shap.py -v --tb=short
"""

import pytest
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')


class TestSHAPArtifacts:
    """Test existence of SHAP artifacts"""
    
    def test_shap_explainer_exists(self):
        """Check if SHAP explainer .pkl file is saved"""
        explainer_path = Path('models/trained/shap_explainer.pkl')
        assert explainer_path.exists(), f"SHAP explainer not found at {explainer_path}"
    
    def test_shap_feature_names_exists(self):
        """Check if feature names metadata JSON exists"""
        metadata_path = Path('models/trained/shap_feature_names.json')
        assert metadata_path.exists(), f"Feature metadata not found at {metadata_path}"
    
    def test_district_explanations_exist(self):
        """Check if pre-computed explanations JSON exists"""
        explanations_path = Path('models/shap/district_explanations.json')
        assert explanations_path.exists(), f"District explanations not found at {explanations_path}"
    
    def test_global_summary_plot_exists(self):
        """Check if global summary plot PNG is generated"""
        plot_path = Path('models/shap/global_summary.png')
        assert plot_path.exists(), f"Global summary plot not found at {plot_path}"
    
    def test_waterfall_example_exists(self):
        """Check if example waterfall chart is generated"""
        waterfall_path = Path('models/shap/waterfall_example.png')
        assert waterfall_path.exists(), f"Waterfall example not found at {waterfall_path}"
    
    def test_shap_report_exists(self):
        """Check if SHAP report JSON exists"""
        report_path = Path('models/shap/shap_report.json')
        assert report_path.exists(), f"SHAP report not found at {report_path}"


class TestSHAPExplainer:
    """Test SHAP explainer functionality"""
    
    def test_explainer_can_load(self):
        """Test that SHAP explainer can be loaded"""
        explainer_path = Path('models/trained/shap_explainer.pkl')
        explainer = joblib.load(explainer_path)
        assert explainer is not None, "Explainer loaded as None"
    
    def test_explainer_has_expected_value(self):
        """Test that explainer has expected_value attribute"""
        explainer = joblib.load('models/trained/shap_explainer.pkl')
        assert hasattr(explainer, 'expected_value'), "Explainer missing expected_value"
    
    def test_feature_metadata_structure(self):
        """Test feature metadata JSON structure"""
        with open('models/trained/shap_feature_names.json') as f:
            metadata = json.load(f)
        
        required_keys = ['feature_names', 'feature_display_names', 'num_features']
        for key in required_keys:
            assert key in metadata, f"Missing key in metadata: {key}"
        
        assert isinstance(metadata['feature_names'], list), "feature_names should be a list"
        assert isinstance(metadata['feature_display_names'], dict), "feature_display_names should be a dict"
        assert metadata['num_features'] == len(metadata['feature_names']), "num_features mismatch"
    
    def test_feature_names_count(self):
        """Test that feature count matches expected (19 features)"""
        with open('models/trained/shap_feature_names.json') as f:
            metadata = json.load(f)
        
        num_features = metadata['num_features']
        assert num_features == 19, f"Expected 19 features, got {num_features}"


class TestSHAPExplanations:
    """Test district explanations"""
    
    def test_explanations_not_empty(self):
        """Test that explanations JSON is not empty"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        assert len(explanations) > 0, "No explanations generated"
    
    def test_explanation_structure(self):
        """Validate explanation JSON structure"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        # Check structure of first explanation
        first_district = list(explanations.values())[0]
        required_keys = [
            'district', 
            'flood_probability', 
            'risk_class', 
            'top_drivers',
            'all_drivers',
            'explanation_text'
        ]
        
        for key in required_keys:
            assert key in first_district, f"Missing key: {key}"
    
    def test_top_drivers_count(self):
        """Test that top_drivers has 3 entries"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        first_district = list(explanations.values())[0]
        assert len(first_district['top_drivers']) == 3, "top_drivers should have 3 entries"
    
    def test_all_drivers_count(self):
        """Test that all_drivers has 5 entries"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        first_district = list(explanations.values())[0]
        assert len(first_district['all_drivers']) == 5, "all_drivers should have 5 entries"
    
    def test_driver_structure(self):
        """Test structure of individual drivers"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        first_district = list(explanations.values())[0]
        driver = first_district['top_drivers'][0]
        
        required_keys = [
            'feature',
            'display_name',
            'shap_value',
            'feature_value',
            'contribution_pct',
            'impact'
        ]
        
        for key in required_keys:
            assert key in driver, f"Driver missing key: {key}"
    
    def test_contribution_percentages_reasonable(self):
        """Test that contribution percentages are between 0 and 100"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        for district_data in explanations.values():
            for driver in district_data['top_drivers']:
                contrib = driver['contribution_pct']
                assert 0 <= contrib <= 100, f"Invalid contribution: {contrib}%"
    
    def test_flood_probability_range(self):
        """Test that flood probabilities are between 0 and 100"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        for district_data in explanations.values():
            prob = district_data['flood_probability']
            assert 0 <= prob <= 100, f"Invalid probability: {prob}"
    
    def test_risk_class_valid(self):
        """Test that risk classes are valid"""
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        valid_classes = ['Low', 'Medium', 'Medium-High', 'High']
        
        for district_data in explanations.values():
            risk_class = district_data['risk_class']
            assert risk_class in valid_classes, f"Invalid risk class: {risk_class}"


class TestSHAPHelpers:
    """Test SHAP helper functions"""
    
    def test_get_shap_explanation(self):
        """Test get_shap_explanation() function"""
        from models.shap_helpers import get_shap_explanation
        
        # Load explanations to get a valid district name
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        if explanations:
            district_name = list(explanations.keys())[0]
            explanation = get_shap_explanation(district_name)
            
            assert explanation is not None, f"Failed to get explanation for {district_name}"
            assert explanation['district'] == district_name, "District name mismatch"
            assert 'top_drivers' in explanation, "Missing top_drivers"
    
    def test_get_shap_explanation_invalid_district(self):
        """Test get_shap_explanation() with invalid district"""
        from models.shap_helpers import get_shap_explanation
        
        explanation = get_shap_explanation("NonExistentDistrict123")
        assert explanation is None, "Should return None for invalid district"
    
    def test_get_all_explanations(self):
        """Test get_all_explanations() function"""
        from models.shap_helpers import get_all_explanations
        
        explanations = get_all_explanations()
        assert isinstance(explanations, dict), "Should return a dictionary"
        assert len(explanations) > 0, "Should return non-empty dictionary"
    
    def test_get_feature_importance(self):
        """Test get_feature_importance() function"""
        from models.shap_helpers import get_feature_importance
        
        importance = get_feature_importance(top_n=5)
        assert isinstance(importance, list), "Should return a list"
        assert len(importance) <= 5, "Should return at most 5 features"
        
        if importance:
            # Check structure
            first_feat = importance[0]
            assert 'feature' in first_feat, "Missing 'feature' key"
            assert 'display_name' in first_feat, "Missing 'display_name' key"
            assert 'avg_contribution' in first_feat, "Missing 'avg_contribution' key"
            
            # Check sorting (descending)
            if len(importance) > 1:
                assert importance[0]['avg_contribution'] >= importance[1]['avg_contribution'], \
                    "Features not sorted by importance"
    
    def test_format_explanation_for_display(self):
        """Test format_explanation_for_display() function"""
        from models.shap_helpers import get_shap_explanation, format_explanation_for_display
        
        # Get first explanation
        with open('models/shap/district_explanations.json') as f:
            explanations = json.load(f)
        
        if explanations:
            district_name = list(explanations.keys())[0]
            explanation = get_shap_explanation(district_name)
            
            formatted = format_explanation_for_display(explanation)
            assert isinstance(formatted, str), "Should return a string"
            assert len(formatted) > 0, "Should return non-empty string"
            assert district_name in formatted, "Formatted text should include district name"


class TestSHAPVisualization:
    """Test SHAP visualization outputs"""
    
    def test_global_summary_is_image(self):
        """Test that global summary is a valid image file"""
        plot_path = Path('models/shap/global_summary.png')
        
        # Check file size (should be > 10KB for a real plot)
        file_size = plot_path.stat().st_size
        assert file_size > 10000, f"Plot file too small ({file_size} bytes), may be corrupted"
    
    def test_waterfall_is_image(self):
        """Test that waterfall chart is a valid image file"""
        waterfall_path = Path('models/shap/waterfall_example.png')
        
        # Check file size
        file_size = waterfall_path.stat().st_size
        assert file_size > 10000, f"Waterfall file too small ({file_size} bytes), may be corrupted"
    
    def test_shap_report_structure(self):
        """Test SHAP report JSON structure"""
        with open('models/shap/shap_report.json') as f:
            report = json.load(f)
        
        required_keys = [
            'total_districts_explained',
            'explainer_type',
            'background_samples',
            'features_analyzed',
            'artifacts_generated'
        ]
        
        for key in required_keys:
            assert key in report, f"Report missing key: {key}"
        
        assert report['total_districts_explained'] > 0, "No districts explained"
        assert report['features_analyzed'] == 19, f"Expected 19 features, got {report['features_analyzed']}"


class TestSHAPIntegration:
    """Integration tests with model and data"""
    
    def test_explainer_works_with_sample_data(self):
        """Test that explainer can compute SHAP values for sample data"""
        # Load explainer
        explainer = joblib.load('models/trained/shap_explainer.pkl')
        
        # Load feature metadata
        with open('models/trained/shap_feature_names.json') as f:
            metadata = json.load(f)
        feature_cols = metadata['feature_names']
        
        # Create sample data (random values)
        sample_data = pd.DataFrame(
            np.random.randn(1, len(feature_cols)),
            columns=feature_cols
        )
        
        # Compute SHAP values (should not raise error)
        try:
            shap_values = explainer.shap_values(sample_data)
            assert shap_values is not None, "SHAP values should not be None"
        except Exception as e:
            pytest.fail(f"Explainer failed on sample data: {e}")
    
    def test_live_explanation_generation(self):
        """Test live SHAP explanation generation"""
        from models.shap_helpers import generate_live_shap_explanation
        
        # Create sample input data
        sample_input = pd.DataFrame({
            'date': ['2023-11-15'],
            'district': ['Chennai'],
            'rainfall_mm': [185.0],
            'river_level_m': [3.2],
            'soil_moisture': [0.78],
            'humidity_pct': [89.0],
            'reservoir_pct': [67.0],
            'rainfall_7d': [425.0],
            'elevation_m': [7.0]
        })
        
        try:
            explanation = generate_live_shap_explanation(sample_input)
            
            assert 'top_drivers' in explanation, "Missing top_drivers"
            assert 'explanation_text' in explanation, "Missing explanation_text"
            assert len(explanation['top_drivers']) == 3, "Should have 3 top drivers"
            
        except Exception as e:
            pytest.fail(f"Live explanation generation failed: {e}")


# Test execution summary
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom test summary"""
    if exitstatus == 0:
        print("\n" + "=" * 70)
        print("✅ ALL SHAP TESTS PASSED!")
        print("=" * 70)
        print("SHAP Module Status: ✅ Fully Operational")
        print("Ready for: Agent 4 (Backend API) integration")
        print("Ready for: Agent 3 (XAI Panel) integration")
        print("=" * 70)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
