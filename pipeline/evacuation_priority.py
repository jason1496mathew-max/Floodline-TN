"""
Evacuation Priority Calculator

Combines flood risk predictions with demographic vulnerability to compute
evacuation priority scores for disaster response planning.

Formula: Priority = 0.5 × Flood Risk + 0.5 × Vulnerability Index

Used by Feature 7: Priority Evacuation Scoring
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


def calculate_evacuation_priority(flood_risk: float, vulnerability_index: float) -> float:
    """
    Combine flood risk and vulnerability into evacuation priority score
    
    Args:
        flood_risk: Flood probability 0-100
        vulnerability_index: Demographic vulnerability 0-100
    
    Returns:
        Priority score 0-100 (100 = highest priority)
    
    Example:
        >>> calculate_evacuation_priority(85, 75)
        80.0
        >>> calculate_evacuation_priority(30, 20)
        25.0
    """
    # Equal weight to both factors
    priority = (0.5 * flood_risk) + (0.5 * vulnerability_index)
    
    return round(priority, 2)


def get_priority_level(priority_score: float) -> str:
    """
    Convert numeric priority to categorical level
    
    Args:
        priority_score: Priority score 0-100
    
    Returns:
        Priority level: 'Critical', 'High', 'Medium', 'Low'
    """
    if priority_score >= 80:
        return 'Critical'
    elif priority_score >= 60:
        return 'High'
    elif priority_score >= 40:
        return 'Medium'
    else:
        return 'Low'


def get_top_priority_districts(
    flood_predictions: pd.DataFrame,
    n: int = 10,
    vulnerability_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Get top N districts requiring evacuation priority
    
    Args:
        flood_predictions: DataFrame with columns ['district_name', 'flood_probability']
        n: Number of top priority districts to return
        vulnerability_file: Path to vulnerability CSV (optional)
    
    Returns:
        DataFrame sorted by evacuation priority with columns:
        - district_name
        - flood_probability
        - vulnerability_index
        - evacuation_priority
        - priority_level
        - elderly_pct
        - population
    """
    # Load vulnerability data
    if vulnerability_file is None:
        data_path = Path(__file__).parent.parent / 'data' / 'demographic'
        vulnerability_file = data_path / 'vulnerability_index.csv'
    
    if not Path(vulnerability_file).exists():
        raise FileNotFoundError(
            f"Vulnerability data not found at {vulnerability_file}\n"
            "Run: python scripts/generate_vulnerability_data.py"
        )
    
    vulnerability_df = pd.read_csv(vulnerability_file)
    
    # Merge flood risk with vulnerability
    merged = flood_predictions.merge(
        vulnerability_df[[
            'district_name', 'vulnerability_index', 'vulnerability_level',
            'elderly_pct', 'population', 'population_density'
        ]],
        on='district_name',
        how='left'
    )
    
    # Check for unmatched districts
    unmatched = merged[merged['vulnerability_index'].isna()]
    if len(unmatched) > 0:
        print(f"⚠️  Warning: {len(unmatched)} districts not found in vulnerability data")
        print(f"   Unmatched districts: {unmatched['district_name'].tolist()}")
    
    # Calculate evacuation priority
    merged['evacuation_priority'] = merged.apply(
        lambda row: calculate_evacuation_priority(
            row['flood_probability'], 
            row['vulnerability_index']
        ) if pd.notna(row['vulnerability_index']) else np.nan,
        axis=1
    )
    
    # Add priority level
    merged['priority_level'] = merged['evacuation_priority'].apply(
        lambda x: get_priority_level(x) if pd.notna(x) else 'Unknown'
    )
    
    # Sort by priority (highest first)
    merged = merged.sort_values('evacuation_priority', ascending=False, na_position='last')
    
    # Return top N
    top_priority = merged.head(n)
    
    return top_priority[[
        'district_name', 'flood_probability', 'vulnerability_index',
        'evacuation_priority', 'priority_level', 'elderly_pct', 
        'population', 'population_density'
    ]]


def get_top_priority_taluks(
    flood_predictions: pd.DataFrame,
    n: int = 10,
    taluk_vulnerability_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Get top N taluks/sub-districts requiring evacuation priority
    
    Args:
        flood_predictions: DataFrame with columns ['taluk_name', 'district_name', 'flood_probability']
        n: Number of top priority taluks to return
        taluk_vulnerability_file: Path to taluk vulnerability CSV (optional)
    
    Returns:
        DataFrame sorted by evacuation priority
    """
    # Load taluk vulnerability data
    if taluk_vulnerability_file is None:
        data_path = Path(__file__).parent.parent / 'data' / 'demographic'
        taluk_vulnerability_file = data_path / 'taluk_vulnerability.csv'
    
    if not Path(taluk_vulnerability_file).exists():
        raise FileNotFoundError(
            f"Taluk vulnerability data not found at {taluk_vulnerability_file}\n"
            "Run: python scripts/generate_taluk_vulnerability.py"
        )
    
    taluks_df = pd.read_csv(taluk_vulnerability_file)
    
    # Merge flood risk with vulnerability
    merged = flood_predictions.merge(
        taluks_df[['taluk_name', 'district_name', 'vulnerability_index', 'vulnerability_level']],
        on=['taluk_name', 'district_name'],
        how='left'
    )
    
    # Calculate evacuation priority
    merged['evacuation_priority'] = merged.apply(
        lambda row: calculate_evacuation_priority(
            row['flood_probability'], 
            row['vulnerability_index']
        ) if pd.notna(row['vulnerability_index']) else np.nan,
        axis=1
    )
    
    # Add priority level
    merged['priority_level'] = merged['evacuation_priority'].apply(
        lambda x: get_priority_level(x) if pd.notna(x) else 'Unknown'
    )
    
    # Sort by priority
    merged = merged.sort_values('evacuation_priority', ascending=False, na_position='last')
    
    # Return top N
    return merged.head(n)


def generate_evacuation_report(flood_predictions: pd.DataFrame) -> dict:
    """
    Generate comprehensive evacuation priority report
    
    Args:
        flood_predictions: DataFrame with flood probability predictions
    
    Returns:
        Dictionary with evacuation statistics and recommendations
    """
    top_districts = get_top_priority_districts(flood_predictions, n=10)
    
    report = {
        "total_districts_analyzed": len(flood_predictions),
        "critical_priority": len(top_districts[top_districts['priority_level'] == 'Critical']),
        "high_priority": len(top_districts[top_districts['priority_level'] == 'High']),
        "top_10_districts": top_districts[[
            'district_name', 'evacuation_priority', 'priority_level'
        ]].to_dict('records'),
        "total_population_at_risk": int(top_districts['population'].sum()),
        "elderly_population_at_risk": int((top_districts['population'] * top_districts['elderly_pct'] / 100).sum()),
        "recommendations": []
    }
    
    # Add recommendations based on priority levels
    critical = top_districts[top_districts['priority_level'] == 'Critical']
    if len(critical) > 0:
        report['recommendations'].append({
            "level": "CRITICAL",
            "action": "Immediate evacuation required",
            "districts": critical['district_name'].tolist()
        })
    
    high = top_districts[top_districts['priority_level'] == 'High']
    if len(high) > 0:
        report['recommendations'].append({
            "level": "HIGH",
            "action": "Prepare evacuation resources",
            "districts": high['district_name'].tolist()
        })
    
    return report


# CLI interface for testing
def main():
    """
    Test evacuation priority calculator with mock flood predictions
    """
    print("🚨 Evacuation Priority Calculator - Test Mode")
    print("=" * 60)
    
    # Create mock flood predictions for testing
    print("\n📊 Generating mock flood predictions...")
    
    # Load real district names from vulnerability data
    data_path = Path(__file__).parent.parent / 'data' / 'demographic'
    vulnerability_file = data_path / 'vulnerability_index.csv'
    
    if vulnerability_file.exists():
        vuln_df = pd.read_csv(vulnerability_file)
        district_names = vuln_df['district_name'].tolist()[:10]  # Use first 10
    else:
        # Fallback to hardcoded names
        district_names = ['Chennai', 'Madurai', 'Coimbatore', 'Salem', 
                         'Tiruchirappalli', 'Tirunelveli', 'Erode', 'Vellore']
    
    # Generate random flood probabilities
    np.random.seed(42)
    mock_predictions = pd.DataFrame({
        'district_name': district_names,
        'flood_probability': np.random.uniform(30, 95, len(district_names)).round(2)
    })
    
    print(f"✅ Generated mock predictions for {len(mock_predictions)} districts")
    print()
    
    # Calculate priorities
    print("🔢 Calculating evacuation priorities...")
    try:
        top_10 = get_top_priority_districts(mock_predictions, n=10)
        
        print("✅ Priority calculation complete")
        print()
        print("🚨 TOP 10 EVACUATION PRIORITY AREAS:")
        print("=" * 60)
        
        for idx, row in top_10.iterrows():
            print(f"\n{idx+1}. {row['district_name']} - Priority: {row['evacuation_priority']:.2f} ({row['priority_level']})")
            print(f"   Flood Risk: {row['flood_probability']:.2f}%")
            print(f"   Vulnerability: {row['vulnerability_index']:.2f}")
            print(f"   Population: {row['population']:,}")
            print(f"   Elderly: {row['elderly_pct']:.1f}%")
        
        print()
        print("=" * 60)
        
        # Generate report
        print("\n📋 Generating evacuation report...")
        report = generate_evacuation_report(mock_predictions)
        
        print(f"\n✅ Report Summary:")
        print(f"   Total districts analyzed: {report['total_districts_analyzed']}")
        print(f"   Critical priority: {report['critical_priority']}")
        print(f"   High priority: {report['high_priority']}")
        print(f"   Population at risk: {report['total_population_at_risk']:,}")
        print(f"   Elderly at risk: {report['elderly_population_at_risk']:,}")
        
        if report['recommendations']:
            print(f"\n🎯 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec['level']}: {rec['action']}")
                print(f"      Districts: {', '.join(rec['districts'])}")
        
        print()
        print("=" * 60)
        print("✅ Test complete!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n   Please run vulnerability data generation first:")
        print("   python scripts/generate_vulnerability_data.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
