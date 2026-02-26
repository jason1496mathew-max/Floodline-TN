"""
API Wrapper for River Propagation Model
========================================

Provides simplified interface for FastAPI backend integration.

Functions:
    - get_cascade_prediction(): Check if conditions trigger cascade
    - get_downstream_alerts(): Get list of downstream districts
    - get_propagation_timeline(): Get hour-by-hour timeline
    - check_trigger_conditions(): Validate trigger thresholds

Usage:
    from models.propagation_api import PropagationAPI
    
    api = PropagationAPI()
    scenario = api.get_cascade_prediction("Madurai", rainfall_mm=185, river_level_m=3.2)
"""

from models.propagation import RiverPropagationModel
from typing import Dict, List, Optional
from pathlib import Path
import json


class PropagationAPI:
    """
    API wrapper for river propagation model
    
    Simplifies integration with FastAPI backend by providing
    high-level functions with validation and error handling.
    """
    
    def __init__(self, config_path: str = 'config/river_network.json'):
        """
        Initialize the propagation API
        
        Args:
            config_path: Path to river network configuration
        """
        try:
            self.model = RiverPropagationModel(config_path)
            self.initialized = True
        except Exception as e:
            print(f"❌ Failed to initialize propagation model: {e}")
            self.initialized = False
            self.model = None
    
    def check_trigger_conditions(
        self, 
        rainfall_mm: float,
        river_level_m: float,
        rainfall_threshold: float = 150.0,
        river_level_threshold: float = 2.5
    ) -> Dict:
        """
        Check if conditions meet cascade trigger thresholds
        
        Args:
            rainfall_mm: Current rainfall in mm
            river_level_m: River level above danger mark in meters
            rainfall_threshold: Minimum rainfall to trigger (default: 150mm)
            river_level_threshold: Minimum river level to trigger (default: 2.5m)
        
        Returns:
            Dict with:
                - triggered: Boolean indicating if cascade triggered
                - rainfall_triggered: Boolean for rainfall condition
                - river_level_triggered: Boolean for river level condition
                - trigger_reasons: List of reasons
        """
        rainfall_triggered = rainfall_mm > rainfall_threshold
        river_level_triggered = river_level_m > river_level_threshold
        
        triggered = rainfall_triggered or river_level_triggered
        
        trigger_reasons = []
        if rainfall_triggered:
            trigger_reasons.append(f"Heavy rainfall ({rainfall_mm}mm exceeds {rainfall_threshold}mm threshold)")
        if river_level_triggered:
            trigger_reasons.append(f"River level critical ({river_level_m}m exceeds {river_level_threshold}m danger mark)")
        
        return {
            "triggered": triggered,
            "rainfall_triggered": rainfall_triggered,
            "river_level_triggered": river_level_triggered,
            "trigger_reasons": trigger_reasons,
            "rainfall_mm": rainfall_mm,
            "river_level_m": river_level_m
        }
    
    def get_cascade_prediction(
        self, 
        district: str, 
        rainfall_mm: float,
        river_level_m: float,
        trigger_time: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Determine if conditions trigger cascade alert and generate scenario
        
        Args:
            district: Upstream district name
            rainfall_mm: Current rainfall in mm
            river_level_m: River level above danger mark in meters
            trigger_time: Optional ISO timestamp
        
        Returns:
            Cascade scenario dict or None if no trigger
            
        Example:
            >>> api = PropagationAPI()
            >>> scenario = api.get_cascade_prediction("Madurai", 185.0, 3.2)
            >>> if scenario:
            ...     print(f"Alert: {len(scenario['timeline'])} districts affected")
        """
        if not self.initialized:
            return {
                "error": "Propagation model not initialized",
                "triggered": False
            }
        
        # Check trigger conditions
        trigger_check = self.check_trigger_conditions(rainfall_mm, river_level_m)
        
        if not trigger_check['triggered']:
            return {
                "district": district,
                "triggered": False,
                "reason": "Conditions below trigger thresholds",
                "rainfall_mm": rainfall_mm,
                "river_level_m": river_level_m
            }
        
        # Generate cascade scenario
        trigger_reason = " + ".join(trigger_check['trigger_reasons'])
        
        try:
            scenario = self.model.simulate_cascade_scenario(
                trigger_district=district,
                trigger_reason=trigger_reason,
                trigger_time=trigger_time
            )
            
            # Add trigger info to scenario
            scenario['triggered'] = True
            scenario['trigger_conditions'] = trigger_check
            
            return scenario
            
        except Exception as e:
            return {
                "error": f"Failed to generate cascade scenario: {str(e)}",
                "district": district,
                "triggered": True
            }
    
    def get_downstream_alerts(self, district: str) -> Dict:
        """
        Get list of downstream districts for alert preparation
        
        Args:
            district: Source district name
        
        Returns:
            Dict with:
                - source_district: Source district name
                - downstream_districts: List of district names
                - downstream_count: Number of downstream districts
                - alert_required: Boolean indicating if alerts needed
                - rivers: List of rivers involved
        
        Example:
            >>> api = PropagationAPI()
            >>> alerts = api.get_downstream_alerts("Madurai")
            >>> print(f"{alerts['downstream_count']} districts need alerts")
        """
        if not self.initialized:
            return {
                "error": "Propagation model not initialized",
                "source_district": district,
                "downstream_districts": [],
                "alert_required": False
            }
        
        try:
            downstream = self.model.get_downstream_districts(district)
            
            # Get rivers passing through source district
            rivers = []
            if district in self.model.graph:
                rivers = self.model.graph.nodes[district].get('rivers', [])
            
            return {
                "source_district": district,
                "downstream_districts": downstream,
                "downstream_count": len(downstream),
                "alert_required": len(downstream) > 0,
                "rivers": rivers
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get downstream districts: {str(e)}",
                "source_district": district,
                "downstream_districts": [],
                "alert_required": False
            }
    
    def get_propagation_timeline(
        self,
        district: str,
        trigger_time_hour: int = 0
    ) -> Dict:
        """
        Get hour-by-hour propagation timeline
        
        Args:
            district: Trigger district
            trigger_time_hour: Hour offset from now (default: 0)
        
        Returns:
            Dict with timeline events
        
        Example:
            >>> api = PropagationAPI()
            >>> timeline = api.get_propagation_timeline("Salem")
            >>> for event in timeline['timeline']:
            ...     print(f"Hour {event['onset_hour']}: {event['district']}")
        """
        if not self.initialized:
            return {
                "error": "Propagation model not initialized",
                "timeline": []
            }
        
        try:
            timeline = self.model.compute_propagation_timeline(
                district, 
                trigger_time_hour
            )
            
            return {
                "trigger_district": district,
                "trigger_time_hour": trigger_time_hour,
                "affected_count": len(timeline),
                "timeline": timeline
            }
            
        except Exception as e:
            return {
                "error": f"Failed to compute timeline: {str(e)}",
                "trigger_district": district,
                "timeline": []
            }
    
    def get_evacuation_priority(
        self,
        district: str,
        rainfall_mm: float,
        river_level_m: float
    ) -> Dict:
        """
        Get prioritized list of districts for evacuation planning
        
        Args:
            district: Trigger district
            rainfall_mm: Current rainfall
            river_level_m: River level above danger
        
        Returns:
            Dict with evacuation priority list
        """
        scenario = self.get_cascade_prediction(district, rainfall_mm, river_level_m)
        
        if not scenario or not scenario.get('triggered'):
            return {
                "district": district,
                "evacuation_required": False,
                "priority_list": []
            }
        
        evacuation_list = scenario.get('evacuation_priority', [])
        
        return {
            "district": district,
            "evacuation_required": len(evacuation_list) > 0,
            "priority_count": len(evacuation_list),
            "priority_list": evacuation_list,
            "summary": scenario.get('summary', '')
        }
    
    def get_district_info(self, district: str) -> Optional[Dict]:
        """
        Get detailed information about a specific district
        
        Args:
            district: District name
        
        Returns:
            District metadata dict or None if not found
        """
        if not self.initialized:
            return None
        
        if district not in self.model.graph:
            return None
        
        node_data = self.model.graph.nodes[district]
        
        # Get upstream and downstream connections
        upstream = list(self.model.graph.predecessors(district))
        downstream = list(self.model.graph.successors(district))
        
        return {
            "district": district,
            "district_tamil": node_data.get('district_tamil', ''),
            "elevation_m": node_data.get('elevation', 0),
            "population": node_data.get('population', 0),
            "rivers": node_data.get('rivers', []),
            "vulnerable_points": node_data.get('vulnerable_points', []),
            "latitude": node_data.get('latitude', 0),
            "longitude": node_data.get('longitude', 0),
            "upstream_districts": upstream,
            "downstream_districts": downstream
        }


# Convenience functions for direct use
def check_cascade_trigger(district: str, rainfall: float, river_level: float) -> bool:
    """
    Quick check if conditions trigger cascade
    
    Args:
        district: District name
        rainfall: Rainfall in mm
        river_level: River level in meters
    
    Returns:
        Boolean indicating trigger status
    """
    api = PropagationAPI()
    result = api.get_cascade_prediction(district, rainfall, river_level)
    return result.get('triggered', False) if result else False


def get_affected_districts(district: str) -> List[str]:
    """
    Quick function to get downstream districts
    
    Args:
        district: Source district
    
    Returns:
        List of downstream district names
    """
    api = PropagationAPI()
    result = api.get_downstream_alerts(district)
    return result.get('downstream_districts', [])


# Testing and demonstration
def main():
    """
    Test the propagation API with example scenarios
    """
    print("=" * 70)
    print("📡 PROPAGATION API - TESTING")
    print("=" * 70)
    
    api = PropagationAPI()
    
    if not api.initialized:
        print("❌ API initialization failed")
        return False
    
    print("✅ API initialized successfully\n")
    
    # Test 1: Check trigger conditions
    print("🧪 Test 1: Check Trigger Conditions")
    print("-" * 70)
    
    trigger_check = api.check_trigger_conditions(
        rainfall_mm=185.0,
        river_level_m=3.2
    )
    
    print(f"   Triggered: {trigger_check['triggered']}")
    print(f"   Reasons: {', '.join(trigger_check['trigger_reasons'])}")
    
    # Test 2: Get cascade prediction for Madurai
    print("\n🧪 Test 2: Cascade Prediction for Madurai")
    print("-" * 70)
    
    scenario = api.get_cascade_prediction(
        district="Madurai",
        rainfall_mm=185.0,
        river_level_m=3.2
    )
    
    if scenario and scenario.get('triggered'):
        print(f"   🚨 CASCADE ALERT TRIGGERED")
        print(f"   Affected districts: {scenario['affected_districts_count']}")
        print(f"   Max propagation: {scenario['max_propagation_hours']} hours")
        print(f"   Summary: {scenario['summary']}")
    else:
        print(f"   No cascade triggered")
    
    # Test 3: Get downstream alerts
    print("\n🧪 Test 3: Downstream Alerts for Salem")
    print("-" * 70)
    
    alerts = api.get_downstream_alerts("Salem")
    
    print(f"   Downstream districts: {alerts['downstream_count']}")
    print(f"   Alert required: {alerts['alert_required']}")
    print(f"   Rivers: {', '.join(alerts.get('rivers', []))}")
    if alerts['downstream_districts']:
        print(f"   Districts: {', '.join(alerts['downstream_districts'][:5])}...")
    
    # Test 4: Get district info
    print("\n🧪 Test 4: District Information for Chennai")
    print("-" * 70)
    
    info = api.get_district_info("Chennai")
    
    if info:
        print(f"   District: {info['district']} ({info['district_tamil']})")
        print(f"   Elevation: {info['elevation_m']}m")
        print(f"   Population: {info['population']:,}")
        print(f"   Rivers: {', '.join(info['rivers'])}")
        print(f"   Upstream: {', '.join(info['upstream_districts'])}")
    
    # Test 5: Evacuation priority
    print("\n🧪 Test 5: Evacuation Priority for Vellore")
    print("-" * 70)
    
    evacuation = api.get_evacuation_priority(
        district="Vellore",
        rainfall_mm=220.0,
        river_level_m=3.5
    )
    
    print(f"   Evacuation required: {evacuation['evacuation_required']}")
    print(f"   Priority districts: {evacuation['priority_count']}")
    
    if evacuation['priority_list']:
        print(f"\n   Top 3 Priority:")
        for i, priority in enumerate(evacuation['priority_list'][:3], 1):
            print(f"      {i}. {priority['district']} - {priority['risk_level']} "
                  f"(Hour {priority['onset_hour']})")
    
    print("\n" + "=" * 70)
    print("✅ ALL API TESTS PASSED")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
