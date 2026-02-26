"""
Tests for River Propagation Model
==================================

Test suite for validating graph-based flood propagation modeling.

Test Coverage:
    - River network configuration
    - Graph initialization
    - Downstream district retrieval
    - Propagation timeline generation
    - Cascade scenario simulation
    - Travel time validation
    - API wrapper functions

Run:
    pytest tests/test_propagation.py -v
"""

import pytest
import json
import os
from pathlib import Path
from models.propagation import RiverPropagationModel
from models.propagation_api import PropagationAPI


@pytest.fixture
def config_path():
    """
    Fixture for river network config path
    """
    base_path = Path(__file__).parent.parent
    return str(base_path / 'config' / 'river_network.json')


@pytest.fixture
def propagation_model(config_path):
    """
    Fixture for propagation model instance
    """
    return RiverPropagationModel(config_path)


@pytest.fixture
def propagation_api(config_path):
    """
    Fixture for propagation API instance
    """
    return PropagationAPI(config_path)


class TestRiverNetworkConfig:
    """
    Test river network configuration file
    """
    
    def test_config_exists(self, config_path):
        """
        Test that configuration file exists
        """
        assert os.path.exists(config_path), "config/river_network.json not found"
    
    def test_config_valid_json(self, config_path):
        """
        Test that config is valid JSON
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert 'rivers' in data
    
    def test_config_has_rivers(self, config_path):
        """
        Test that config contains river data
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            rivers = data['rivers']
            assert len(rivers) >= 4, "Should have at least 4 major rivers"
            
            # Check river structure
            river_names = ['Cauvery', 'Vaigai', 'Palar', 'Tamirabarani']
            for river_name in river_names:
                assert river_name in rivers, f"{river_name} missing from config"
    
    def test_config_river_properties(self, config_path):
        """
        Test that rivers have required properties
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            for river_name, river_data in data['rivers'].items():
                assert 'length_km' in river_data
                assert 'average_velocity_kmh' in river_data
                assert 'flow_path' in river_data
                
                # Check flow path structure
                flow_path = river_data['flow_path']
                assert isinstance(flow_path, list)
                assert len(flow_path) > 0
                
                for district in flow_path:
                    assert 'district' in district
                    assert 'elevation' in district
                    assert 'population' in district


class TestGraphInitialization:
    """
    Test graph model initialization
    """
    
    def test_model_initializes(self, propagation_model):
        """
        Test that model initializes successfully
        """
        assert propagation_model is not None
        assert propagation_model.graph is not None
    
    def test_graph_has_nodes(self, propagation_model):
        """
        Test that graph contains district nodes
        """
        assert len(propagation_model.graph.nodes) > 0
        
        # Should have at least 15 unique districts
        assert len(propagation_model.graph.nodes) >= 15
    
    def test_graph_has_edges(self, propagation_model):
        """
        Test that graph contains river flow edges
        """
        assert len(propagation_model.graph.edges) > 0
    
    def test_graph_is_directed(self, propagation_model):
        """
        Test that graph is directed (DiGraph)
        """
        import networkx as nx
        assert isinstance(propagation_model.graph, nx.DiGraph)
    
    def test_node_properties(self, propagation_model):
        """
        Test that nodes have required properties
        """
        # Get a sample node
        nodes = list(propagation_model.graph.nodes(data=True))
        assert len(nodes) > 0
        
        district_name, node_data = nodes[0]
        
        # Check required properties
        assert 'elevation' in node_data
        assert 'population' in node_data
        assert 'rivers' in node_data
        assert isinstance(node_data['rivers'], list)
    
    def test_edge_properties(self, propagation_model):
        """
        Test that edges have required properties
        """
        edges = list(propagation_model.graph.edges(data=True))
        assert len(edges) > 0
        
        source, target, edge_data = edges[0]
        
        # Check required properties
        assert 'river' in edge_data
        assert 'distance_km' in edge_data
        assert 'travel_time_hours' in edge_data
        assert edge_data['travel_time_hours'] > 0


class TestDownstreamRetrieval:
    """
    Test downstream district retrieval
    """
    
    def test_get_downstream_districts_salem(self, propagation_model):
        """
        Test downstream districts from Salem (on Cauvery)
        """
        downstream = propagation_model.get_downstream_districts("Salem")
        
        assert isinstance(downstream, list)
        
        # Salem should have downstream districts on Cauvery
        expected_downstream = ["Erode", "Karur", "Tiruchirappalli", 
                               "Thanjavur", "Nagapattinam"]
        
        for district in expected_downstream:
            assert district in downstream, f"{district} should be downstream of Salem"
    
    def test_get_downstream_districts_madurai(self, propagation_model):
        """
        Test downstream districts from Madurai (on Vaigai)
        """
        downstream = propagation_model.get_downstream_districts("Madurai")
        
        assert isinstance(downstream, list)
        
        # Madurai should have downstream districts on Vaigai
        expected_downstream = ["Sivaganga", "Ramanathapuram"]
        
        for district in expected_downstream:
            assert district in downstream, f"{district} should be downstream of Madurai"
    
    def test_get_downstream_terminal_district(self, propagation_model):
        """
        Test terminal district (no downstream)
        """
        # Nagapattinam is terminal on Cauvery
        downstream = propagation_model.get_downstream_districts("Nagapattinam")
        
        assert isinstance(downstream, list)
        assert len(downstream) == 0, "Terminal district should have no downstream"
    
    def test_get_downstream_invalid_district(self, propagation_model):
        """
        Test invalid district name
        """
        downstream = propagation_model.get_downstream_districts("InvalidDistrict")
        
        assert isinstance(downstream, list)
        assert len(downstream) == 0


class TestPropagationTimeline:
    """
    Test propagation timeline generation
    """
    
    def test_timeline_salem(self, propagation_model):
        """
        Test timeline generation from Salem
        """
        timeline = propagation_model.compute_propagation_timeline("Salem", trigger_time_hour=0)
        
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        # First entry should be trigger district
        assert timeline[0]['district'] == "Salem"
        assert timeline[0]['onset_hour'] == 0
        
        # Timeline should be sorted by onset hour
        for i in range(len(timeline) - 1):
            assert timeline[i]['onset_hour'] <= timeline[i + 1]['onset_hour']
    
    def test_timeline_has_required_fields(self, propagation_model):
        """
        Test that timeline entries have required fields
        """
        timeline = propagation_model.compute_propagation_timeline("Madurai", trigger_time_hour=0)
        
        for entry in timeline:
            assert 'district' in entry
            assert 'onset_hour' in entry
            assert 'risk_level' in entry
            assert 'travel_time_from_source' in entry
    
    def test_timeline_risk_categorization(self, propagation_model):
        """
        Test risk level categorization
        """
        timeline = propagation_model.compute_propagation_timeline("Vellore", trigger_time_hour=0)
        
        for entry in timeline:
            risk = entry['risk_level']
            hours = entry['travel_time_from_source']
            
            # Validate risk categories match hours
            if hours < 6:
                assert risk == "Critical", f"<6h should be Critical, got {risk}"
            elif hours < 12:
                assert risk == "High", f"<12h should be High, got {risk}"
            elif hours < 24:
                assert risk == "Medium", f"<24h should be Medium, got {risk}"
            else:
                assert risk == "Low", f">24h should be Low, got {risk}"
    
    def test_timeline_offset(self, propagation_model):
        """
        Test timeline with time offset
        """
        timeline_0 = propagation_model.compute_propagation_timeline("Salem", trigger_time_hour=0)
        timeline_5 = propagation_model.compute_propagation_timeline("Salem", trigger_time_hour=5)
        
        # Onset hours should be offset by 5
        assert timeline_5[0]['onset_hour'] == timeline_0[0]['onset_hour'] + 5


class TestCascadeScenario:
    """
    Test cascade scenario simulation
    """
    
    def test_scenario_generation(self, propagation_model):
        """
        Test complete scenario generation
        """
        scenario = propagation_model.simulate_cascade_scenario(
            trigger_district="Madurai",
            trigger_reason="Heavy rainfall (185mm) in Madurai district"
        )
        
        assert isinstance(scenario, dict)
        
        # Check required fields
        assert 'trigger_district' in scenario
        assert 'trigger_reason' in scenario
        assert 'affected_districts_count' in scenario
        assert 'timeline' in scenario
        assert 'evacuation_priority' in scenario
        assert 'summary' in scenario
    
    def test_scenario_evacuation_priority(self, propagation_model):
        """
        Test evacuation priority ordering
        """
        scenario = propagation_model.simulate_cascade_scenario(
            trigger_district="Salem",
            trigger_reason="Mettur Dam water release"
        )
        
        evacuation_list = scenario['evacuation_priority']
        
        assert isinstance(evacuation_list, list)
        assert len(evacuation_list) > 0
        
        # Should be ordered by onset hour
        for i in range(len(evacuation_list) - 1):
            assert evacuation_list[i]['onset_hour'] <= evacuation_list[i + 1]['onset_hour']
    
    def test_scenario_summary(self, propagation_model):
        """
        Test scenario summary generation
        """
        scenario = propagation_model.simulate_cascade_scenario(
            trigger_district="Vellore",
            trigger_reason="Upstream flood"
        )
        
        summary = scenario['summary']
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Vellore" in summary or scenario['trigger_district'] in summary


class TestTravelTimeValidation:
    """
    Test travel time calculations
    """
    
    def test_travel_times_realistic(self, propagation_model):
        """
        Test that travel times are realistic (not too fast or slow)
        """
        timeline = propagation_model.compute_propagation_timeline("Salem", trigger_time_hour=0)
        
        for entry in timeline:
            travel_time = entry['travel_time_from_source']
            
            # Travel time should be positive
            assert travel_time >= 0
            
            # Travel time should be reasonable (not more than 72 hours for rivers)
            assert travel_time <= 72, f"Excessive travel time: {travel_time}h for {entry['district']}"
    
    def test_travel_time_increases_downstream(self, propagation_model):
        """
        Test that travel time increases as we go downstream
        """
        timeline = propagation_model.compute_propagation_timeline("Dharmapuri", trigger_time_hour=0)
        
        # Get Cauvery districts in order
        cauvery_districts = ["Dharmapuri", "Salem", "Erode", "Karur", 
                             "Tiruchirappalli", "Thanjavur", "Nagapattinam"]
        
        cauvery_timeline = [entry for entry in timeline if entry['district'] in cauvery_districts]
        
        # Sort by position in river
        cauvery_sorted = sorted(cauvery_timeline, key=lambda x: cauvery_districts.index(x['district']))
        
        # Travel time should generally increase
        for i in range(len(cauvery_sorted) - 1):
            assert cauvery_sorted[i]['travel_time_from_source'] <= cauvery_sorted[i + 1]['travel_time_from_source']


class TestPropagationAPI:
    """
    Test API wrapper functions
    """
    
    def test_api_initializes(self, propagation_api):
        """
        Test API initialization
        """
        assert propagation_api is not None
        assert propagation_api.initialized
    
    def test_check_trigger_conditions(self, propagation_api):
        """
        Test trigger condition checking
        """
        # Test triggering conditions
        result = propagation_api.check_trigger_conditions(
            rainfall_mm=185.0,
            river_level_m=3.2
        )
        
        assert result['triggered']
        assert result['rainfall_triggered']
        assert result['river_level_triggered']
        
        # Test non-triggering conditions
        result_low = propagation_api.check_trigger_conditions(
            rainfall_mm=100.0,
            river_level_m=1.5
        )
        
        assert not result_low['triggered']
    
    def test_get_cascade_prediction(self, propagation_api):
        """
        Test cascade prediction function
        """
        scenario = propagation_api.get_cascade_prediction(
            district="Madurai",
            rainfall_mm=185.0,
            river_level_m=3.2
        )
        
        assert scenario is not None
        assert scenario['triggered']
        assert 'timeline' in scenario
        assert 'evacuation_priority' in scenario
    
    def test_get_cascade_prediction_no_trigger(self, propagation_api):
        """
        Test cascade prediction with no trigger
        """
        scenario = propagation_api.get_cascade_prediction(
            district="Chennai",
            rainfall_mm=50.0,
            river_level_m=1.0
        )
        
        assert scenario is not None
        assert not scenario['triggered']
    
    def test_get_downstream_alerts(self, propagation_api):
        """
        Test downstream alert function
        """
        result = propagation_api.get_downstream_alerts("Salem")
        
        assert 'downstream_districts' in result
        assert 'downstream_count' in result
        assert 'alert_required' in result
        
        assert result['downstream_count'] > 0
        assert result['alert_required']
    
    def test_get_propagation_timeline(self, propagation_api):
        """
        Test timeline function
        """
        result = propagation_api.get_propagation_timeline("Madurai", trigger_time_hour=0)
        
        assert 'timeline' in result
        assert 'affected_count' in result
        assert result['affected_count'] > 0
    
    def test_get_evacuation_priority(self, propagation_api):
        """
        Test evacuation priority function
        """
        result = propagation_api.get_evacuation_priority(
            district="Vellore",
            rainfall_mm=220.0,
            river_level_m=3.5
        )
        
        assert 'evacuation_required' in result
        assert 'priority_list' in result
        assert result['evacuation_required']
    
    def test_get_district_info(self, propagation_api):
        """
        Test district info function
        """
        info = propagation_api.get_district_info("Chennai")
        
        assert info is not None
        assert 'district' in info
        assert 'elevation_m' in info
        assert 'population' in info
        assert 'rivers' in info
    
    def test_get_district_info_invalid(self, propagation_api):
        """
        Test district info for invalid district
        """
        info = propagation_api.get_district_info("InvalidDistrict")
        
        assert info is None


class TestGraphVisualization:
    """
    Test graph visualization (non-rendering tests)
    """
    
    def test_visualize_graph_callable(self, propagation_model):
        """
        Test that visualize_graph method exists
        """
        assert hasattr(propagation_model, 'visualize_graph')
        assert callable(propagation_model.visualize_graph)


# Integration tests
class TestIntegration:
    """
    Integration tests for full workflow
    """
    
    def test_full_workflow_madurai(self, propagation_api):
        """
        Test complete workflow from trigger to evacuation
        """
        # Step 1: Check trigger
        trigger = propagation_api.check_trigger_conditions(
            rainfall_mm=185.0,
            river_level_m=3.2
        )
        
        assert trigger['triggered']
        
        # Step 2: Get cascade prediction
        scenario = propagation_api.get_cascade_prediction(
            district="Madurai",
            rainfall_mm=185.0,
            river_level_m=3.2
        )
        
        assert scenario['triggered']
        
        # Step 3: Get downstream alerts
        alerts = propagation_api.get_downstream_alerts("Madurai")
        
        assert alerts['alert_required']
        
        # Step 4: Get evacuation priority
        evacuation = propagation_api.get_evacuation_priority(
            district="Madurai",
            rainfall_mm=185.0,
            river_level_m=3.2
        )
        
        assert evacuation['evacuation_required']
        
        # Verify consistency
        assert scenario['affected_districts_count'] == alerts['downstream_count'] + 1
    
    def test_full_workflow_no_trigger(self, propagation_api):
        """
        Test workflow when conditions don't trigger
        """
        # Non-triggering conditions
        trigger = propagation_api.check_trigger_conditions(
            rainfall_mm=80.0,
            river_level_m=1.2
        )
        
        assert not trigger['triggered']
        
        scenario = propagation_api.get_cascade_prediction(
            district="Chennai",
            rainfall_mm=80.0,
            river_level_m=1.2
        )
        
        assert not scenario['triggered']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
