"""
River Flood Propagation Model for Floodline TN
===============================================

Agent: Agent 1 (Data Pipeline Engineer) - Graph Modeling Phase
Module: 07 - River Propagation Model

This module implements a NetworkX directed graph model to simulate flood
propagation downstream along Tamil Nadu's major river systems.

Key Features:
    - NetworkX DiGraph with districts as nodes, river flows as edges
    - Travel time computation based on distance and flow velocity
    - Cascade timeline generation for downstream districts
    - Risk level estimation based on propagation time
    - Graph visualization

Rivers Modeled:
    - Cauvery (8 districts, 416 km)
    - Vaigai (4 districts, 258 km)
    - Palar (5 districts, 348 km)
    - Tamirabarani (2 districts, 128 km)

Usage:
    from models.propagation import RiverPropagationModel
    
    model = RiverPropagationModel()
    scenario = model.simulate_cascade_scenario("Madurai")
    print(scenario['timeline'])
"""

import networkx as nx
import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class RiverPropagationModel:
    """
    Graph-based river flood propagation model for Tamil Nadu
    
    Attributes:
        graph: NetworkX DiGraph with districts as nodes
        rivers: List of river configuration dicts
        district_info: Dict mapping district names to metadata
    """
    
    def __init__(self, config_path: str = 'config/river_network.json'):
        """
        Initialize the river propagation model
        
        Args:
            config_path: Path to river network JSON configuration
        """
        self.graph = nx.DiGraph()
        self.rivers = []
        self.district_info = {}
        self.config_path = Path(config_path)
        
        self._load_river_network()
        self._build_graph()
    
    def _load_river_network(self) -> None:
        """
        Load river network configuration from JSON file
        
        Raises:
            FileNotFoundError: If config file not found
            json.JSONDecodeError: If JSON is malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"❌ River network config not found: {self.config_path}\n"
                f"   Expected location: config/river_network.json"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"❌ Invalid JSON in river_network.json: {e}",
                e.doc, e.pos
            )
        
        self.rivers = data.get('rivers', [])
        self.metadata = data.get('metadata', {})
        self.propagation_params = data.get('propagation_parameters', {})
        
        if not self.rivers:
            raise ValueError("❌ No rivers found in configuration")
        
        print(f"✅ Loaded {len(self.rivers)} river systems from configuration")
    
    def _build_graph(self) -> None:
        """
        Build directed graph from river network data
        
        Nodes = Districts with elevation and population metadata
        Edges = River flow connections with travel time and distance
        """
        for river in self.rivers:
            river_name = river['name']
            river_name_tamil = river['name_tamil']
            flow_path = river['flow_path']
            velocity = river['avg_flow_velocity_kmh']
            
            # Add nodes for each district in the flow path
            for segment in flow_path:
                district = segment['district']
                
                if not self.graph.has_node(district):
                    # First time seeing this district
                    self.graph.add_node(
                        district,
                        elevation=segment['elevation_m'],
                        population=segment['population'],
                        district_tamil=segment.get('district_tamil', ''),
                        latitude=segment.get('latitude', 0),
                        longitude=segment.get('longitude', 0),
                        vulnerable_points=segment.get('vulnerable_points', []),
                        rivers=[river_name]  # List of rivers passing through
                    )
                    
                    # Store district info for quick lookup
                    self.district_info[district] = {
                        'elevation': segment['elevation_m'],
                        'population': segment['population'],
                        'district_tamil': segment.get('district_tamil', ''),
                        'vulnerable_points': segment.get('vulnerable_points', [])
                    }
                else:
                    # District already in graph (on multiple rivers)
                    self.graph.nodes[district]['rivers'].append(river_name)
            
            # Add edges (directed: upstream → downstream)
            for i in range(len(flow_path) - 1):
                upstream_segment = flow_path[i]
                downstream_segment = flow_path[i + 1]
                
                upstream = upstream_segment['district']
                downstream = downstream_segment['district']
                
                # Calculate distance between consecutive districts
                distance_km = downstream_segment['distance_km'] - upstream_segment['distance_km']
                
                # Calculate travel time (hours) = distance / velocity
                travel_time_hours = distance_km / velocity
                
                # Add directed edge
                self.graph.add_edge(
                    upstream,
                    downstream,
                    river=river_name,
                    river_tamil=river_name_tamil,
                    distance_km=distance_km,
                    travel_time_hours=round(travel_time_hours, 2),
                    weight=travel_time_hours,  # For shortest path algorithms
                    avg_velocity_kmh=velocity
                )
        
        print(f"✅ Built river network graph:")
        print(f"   Nodes (districts): {self.graph.number_of_nodes()}")
        print(f"   Edges (connections): {self.graph.number_of_edges()}")
        
        # Print river summary
        for river in self.rivers:
            districts_count = len(river['flow_path'])
            print(f"   - {river['name']:20s} ({districts_count} districts, {river['length_in_tn_km']} km)")
    
    def get_downstream_districts(self, trigger_district: str) -> List[str]:
        """
        Get all districts downstream from trigger point using graph traversal
        
        Args:
            trigger_district: Name of upstream district
        
        Returns:
            List of downstream district names (sorted by distance)
        """
        if trigger_district not in self.graph:
            print(f"⚠️  District '{trigger_district}' not found in river network")
            return []
        
        # Use NetworkX descendants to find all reachable downstream nodes
        downstream = list(nx.descendants(self.graph, trigger_district))
        
        return downstream
    
    def compute_propagation_timeline(
        self, 
        trigger_district: str, 
        trigger_time_hour: int = 0
    ) -> List[Dict]:
        """
        Compute hour-by-hour propagation timeline for downstream districts
        
        Args:
            trigger_district: Upstream district where flood starts
            trigger_time_hour: Hour when trigger occurs (default: 0 = now)
        
        Returns:
            List of timeline event dicts with:
                - district: District name
                - river: River name
                - path: List of districts in propagation path
                - travel_time_hours: Time from trigger to district
                - onset_hour: Absolute hour when flood reaches district
                - risk_level: Risk category (Critical/High/Medium/Low)
                - distance_km: Total distance from trigger point
        """
        if trigger_district not in self.graph:
            print(f"⚠️  District '{trigger_district}' not found in river network")
            return []
        
        timeline = []
        
        # Get all downstream districts
        downstream_districts = self.get_downstream_districts(trigger_district)
        
        if not downstream_districts:
            print(f"   No downstream districts found from {trigger_district}")
            return []
        
        # For each downstream district, find shortest path (minimum travel time)
        for district in downstream_districts:
            try:
                # Find shortest path by travel time
                path = nx.shortest_path(
                    self.graph, 
                    source=trigger_district, 
                    target=district,
                    weight='weight'
                )
                
                # Calculate cumulative travel time and distance
                travel_time = 0
                total_distance = 0
                
                for i in range(len(path) - 1):
                    edge_data = self.graph[path[i]][path[i + 1]]
                    travel_time += edge_data['travel_time_hours']
                    total_distance += edge_data['distance_km']
                
                # Determine risk onset time
                onset_hour = trigger_time_hour + int(travel_time)
                
                # Get district metadata
                district_data = self.graph.nodes[district]
                
                # Timeline event
                timeline.append({
                    "district": district,
                    "district_tamil": district_data.get('district_tamil', ''),
                    "river": self.graph[path[-2]][path[-1]]['river'],
                    "river_tamil": self.graph[path[-2]][path[-1]]['river_tamil'],
                    "path": path,
                    "travel_time_hours": round(travel_time, 1),
                    "onset_hour": onset_hour,
                    "distance_km": round(total_distance, 1),
                    "elevation_m": district_data.get('elevation', 0),
                    "population": district_data.get('population', 0),
                    "vulnerable_points": district_data.get('vulnerable_points', []),
                    "risk_level": self._estimate_risk_level(travel_time)
                })
            
            except nx.NetworkXNoPath:
                # No path found (shouldn't happen if descendants worked correctly)
                continue
        
        # Sort by onset time (earliest first)
        timeline.sort(key=lambda x: x['travel_time_hours'])
        
        return timeline
    
    def _estimate_risk_level(self, travel_time_hours: float) -> str:
        """
        Estimate risk level based on propagation time
        
        Closer districts = higher risk due to less evacuation time
        
        Args:
            travel_time_hours: Time for flood to reach district
        
        Returns:
            Risk level: "Critical", "High", "Medium", or "Low"
        """
        if travel_time_hours < 6:
            return "Critical"
        elif travel_time_hours < 12:
            return "High"
        elif travel_time_hours < 24:
            return "Medium"
        else:
            return "Low"
    
    def simulate_cascade_scenario(
        self, 
        trigger_district: str,
        trigger_reason: str = "Heavy rainfall + high river level",
        trigger_time: Optional[str] = None
    ) -> Dict:
        """
        Generate complete cascade scenario for demo and API integration
        
        Args:
            trigger_district: Upstream trigger point
            trigger_reason: Human-readable trigger description
            trigger_time: ISO timestamp of trigger (default: now)
        
        Returns:
            Complete scenario dict with:
                - trigger_district: Trigger location
                - trigger_reason: Why flood started
                - trigger_time: When it started
                - affected_districts_count: Number of downstream districts
                - max_propagation_hours: Maximum travel time
                - timeline: List of propagation events
                - rivers_involved: List of river names
                - summary: Human-readable summary
                - evacuation_priority: Prioritized district list
        """
        if trigger_time is None:
            trigger_time = datetime.now().isoformat()
        
        # Compute timeline
        timeline = self.compute_propagation_timeline(trigger_district)
        
        if not timeline:
            return {
                "trigger_district": trigger_district,
                "trigger_reason": trigger_reason,
                "trigger_time": trigger_time,
                "affected_districts_count": 0,
                "max_propagation_hours": 0,
                "timeline": [],
                "rivers_involved": [],
                "summary": f"No downstream districts affected by flood at {trigger_district}.",
                "evacuation_priority": []
            }
        
        # Extract unique rivers
        rivers_involved = list(set([event['river'] for event in timeline]))
        
        # Maximum propagation time
        max_time = max([event['travel_time_hours'] for event in timeline])
        
        # Create evacuation priority (critical districts first)
        evacuation_priority = []
        for event in timeline:
            if event['risk_level'] in ['Critical', 'High']:
                evacuation_priority.append({
                    'district': event['district'],
                    'onset_hour': event['onset_hour'],
                    'risk_level': event['risk_level'],
                    'population': event['population']
                })
        
        # Sort evacuation priority by onset time
        evacuation_priority.sort(key=lambda x: x['onset_hour'])
        
        # Build scenario
        scenario = {
            "trigger_district": trigger_district,
            "trigger_district_tamil": self.graph.nodes[trigger_district].get('district_tamil', ''),
            "trigger_reason": trigger_reason,
            "trigger_time": trigger_time,
            "affected_districts_count": len(timeline),
            "max_propagation_hours": round(max_time, 1),
            "timeline": timeline,
            "rivers_involved": rivers_involved,
            "rivers_involved_tamil": [self.graph[timeline[0]['path'][-2]][timeline[0]['path'][-1]]['river_tamil']],
            "summary": f"Flood event at {trigger_district} affects {len(timeline)} downstream districts over {max_time:.1f} hours via {', '.join(rivers_involved)}.",
            "evacuation_priority": evacuation_priority,
            "generated_at": datetime.now().isoformat()
        }
        
        return scenario
    
    def visualize_graph(
        self, 
        output_path: str = 'models/propagation_graph.png',
        highlight_path: Optional[List[str]] = None
    ) -> Path:
        """
        Generate visual representation of river network graph
        
        Args:
            output_path: Where to save the PNG file
            highlight_path: Optional path to highlight (e.g., cascade route)
        
        Returns:
            Path to saved visualization
        """
        plt.figure(figsize=(16, 12))
        
        # Use spring layout for automatic positioning
        pos = nx.spring_layout(self.graph, k=3, iterations=100, seed=42)
        
        # Draw nodes
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            # Color by elevation (higher = darker)
            elevation = self.graph.nodes[node]['elevation']
            node_colors.append(elevation)
            
            # Size by population
            population = self.graph.nodes[node]['population']
            node_sizes.append(max(500, population / 5000))
        
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            cmap='YlOrRd',
            alpha=0.8,
            edgecolors='black',
            linewidths=2
        )
        
        # Draw edges
        edge_colors = ['#1976D2' if self.graph[u][v]['river'] == 'Cauvery' 
                       else '#388E3C' if self.graph[u][v]['river'] == 'Vaigai'
                       else '#F57C00' if self.graph[u][v]['river'] == 'Palar'
                       else '#7B1FA2'
                       for u, v in self.graph.edges()]
        
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color=edge_colors,
            arrows=True,
            arrowsize=25,
            width=3,
            alpha=0.7,
            arrowstyle='-|>',
            connectionstyle='arc3,rad=0.1'
        )
        
        # Highlight path if provided
        if highlight_path and len(highlight_path) > 1:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                          for i in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=path_edges,
                edge_color='red',
                width=5,
                alpha=1.0,
                arrows=True,
                arrowsize=30
            )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_weight='bold',
            font_family='sans-serif'
        )
        
        # Draw edge labels (travel time)
        edge_labels = {}
        for u, v, d in self.graph.edges(data=True):
            edge_labels[(u, v)] = f"{d['travel_time_hours']:.1f}h"
        
        nx.draw_networkx_edge_labels(
            self.graph, pos,
            edge_labels,
            font_size=8,
            font_color='darkred'
        )
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#1976D2', markersize=10, 
                      label='Cauvery', linewidth=0),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#388E3C', markersize=10, 
                      label='Vaigai', linewidth=0),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#F57C00', markersize=10, 
                      label='Palar', linewidth=0),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#7B1FA2', markersize=10, 
                      label='Tamirabarani', linewidth=0)
        ]
        plt.legend(handles=legend_elements, loc='upper right', fontsize=12)
        
        # Title and formatting
        plt.title(
            "Floodline TN - River Network Propagation Graph\n"
            "Node Color: Elevation | Node Size: Population | Edge Labels: Travel Time (hours)",
            fontsize=16, fontweight='bold', pad=20
        )
        plt.axis('off')
        plt.tight_layout()
        
        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Graph visualization saved to {output_path}")
        
        return output_path


def main():
    """
    Test the river propagation model with example scenarios
    """
    print("=" * 70)
    print("📡 RIVER PROPAGATION MODEL - FLOODLINE TN")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Initialize model
        print("🔄 Initializing River Propagation Model...")
        print("-" * 70)
        model = RiverPropagationModel()
        
        # Visualize graph
        print("\n📊 Generating Graph Visualization...")
        print("-" * 70)
        model.visualize_graph()
        
        # Test Scenario 1: Madurai flood (Vaigai river)
        print("\n\n🌊 SCENARIO 1: Madurai Flood Event (Vaigai River)")
        print("=" * 70)
        
        scenario1 = model.simulate_cascade_scenario(
            trigger_district="Madurai",
            trigger_reason="Vaigai river level 3.2m above danger + 185mm rainfall in 24 hours"
        )
        
        print(f"\n📊 Scenario Summary:")
        print(f"   Trigger: {scenario1['trigger_district']} ({scenario1['trigger_district_tamil']})")
        print(f"   Reason: {scenario1['trigger_reason']}")
        print(f"   Affected districts: {scenario1['affected_districts_count']}")
        print(f"   Max propagation time: {scenario1['max_propagation_hours']} hours")
        print(f"   Rivers involved: {', '.join(scenario1['rivers_involved'])}")
        
        print(f"\n⏱️  Propagation Timeline:")
        print("-" * 70)
        print(f"{'Hour':>6} | {'District':<25} | {'Risk':>10} | {'Distance':>10}")
        print("-" * 70)
        for event in scenario1['timeline']:
            print(f"{event['onset_hour']:6d} | {event['district']:<25} | "
                  f"{event['risk_level']:>10} | {event['distance_km']:>9.1f} km")
        
        # Save scenario to JSON
        output_path1 = Path('models/propagation_scenario_madurai.json')
        output_path1.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path1, 'w', encoding='utf-8') as f:
            json.dump(scenario1, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Scenario saved to {output_path1}")
        
        # Test Scenario 2: Salem (Mettur Dam on Cauvery)
        print("\n\n🌊 SCENARIO 2: Mettur Dam Release (Cauvery River)")
        print("=" * 70)
        
        scenario2 = model.simulate_cascade_scenario(
            trigger_district="Salem",
            trigger_reason="Mettur Dam at 90% capacity + 200mm overnight rainfall upstream"
        )
        
        print(f"\n📊 Scenario Summary:")
        print(f"   Trigger: {scenario2['trigger_district']}")
        print(f"   Affected districts: {scenario2['affected_districts_count']}")
        print(f"   Max propagation time: {scenario2['max_propagation_hours']} hours")
        print(f"   Rivers involved: {', '.join(scenario2['rivers_involved'])}")
        
        print(f"\n⏱️  First 5 Affected Districts:")
        print("-" * 70)
        for event in scenario2['timeline'][:5]:
            print(f"   Hour {event['onset_hour']:3d}: {event['district']:20s} "
                  f"({event['risk_level']:8s}) - Population: {event['population']:,}")
        
        # Save scenario 2
        output_path2 = Path('models/propagation_scenario_salem.json')
        with open(output_path2, 'w', encoding='utf-8') as f:
            json.dump(scenario2, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Scenario saved to {output_path2}")
        
        # Test Scenario 3: Chennai (Palar River - 2015 floods reference)
        print("\n\n🌊 SCENARIO 3: Vellore Trigger (Palar River)")
        print("=" * 70)
        
        scenario3 = model.simulate_cascade_scenario(
            trigger_district="Vellore",
            trigger_reason="Upstream Karnataka release + heavy monsoon (250mm)"
        )
        
        print(f"\n📊 Scenario Summary:")
        print(f"   Affected districts: {scenario3['affected_districts_count']}")
        print(f"   Critical/High risk districts: {len(scenario3['evacuation_priority'])}")
        
        if scenario3['evacuation_priority']:
            print(f"\n🚨 Evacuation Priority:")
            print("-" * 70)
            for priority in scenario3['evacuation_priority'][:3]:
                print(f"   {priority['district']:20s} - {priority['risk_level']:8s} "
                      f"(Population: {priority['population']:,})")
        
        # Print summary statistics
        print("\n\n📈 MODEL STATISTICS")
        print("=" * 70)
        print(f"   Total districts in network: {model.graph.number_of_nodes()}")
        print(f"   Total river connections: {model.graph.number_of_edges()}")
        print(f"   Rivers modeled: {len(model.rivers)}")
        
        # Print rivers summary
        print(f"\n   Rivers Coverage:")
        for river in model.rivers:
            print(f"   - {river['name']:15s}: {len(river['flow_path'])} districts, "
                  f"{river['length_in_tn_km']} km, {river['avg_flow_velocity_kmh']} km/h")
        
        print("\n" + "=" * 70)
        print("✅ RIVER PROPAGATION MODEL COMPLETE!")
        print("=" * 70)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nGenerated Files:")
        print(f"   - models/propagation_graph.png")
        print(f"   - models/propagation_scenario_madurai.json")
        print(f"   - models/propagation_scenario_salem.json")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ RIVER PROPAGATION MODEL FAILED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
