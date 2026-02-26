"""
Tamil Translation Module for Floodline TN
==========================================

Tamil translations for alert messages, district names, and action instructions.

Features:
    - Alert level translations
    - District name translations
    - Action instructions (Tamil + English)
    - Parameter formatting utilities

Author: Floodline TN Team
Date: February 2026
"""

from typing import Dict


# Tamil translations dictionary
TAMIL_TRANSLATIONS = {
    # Alert levels
    "advisory": "ஆலோசனை",
    "watch": "கண்காணிப்பு",
    "warning": "எச்சரிக்கை",
    "emergency": "அவசரநிலை",
    
    # Common terms
    "flood_risk": "வெள்ள அபாயம்",
    "high": "அதிகமாக",
    "medium": "நடுத்தர",
    "low": "குறைவாக",
    "very_high": "மிக அதிகமாக",
    "reason": "காரணம்",
    "probability": "நிகழ்தகவு",
    "district": "மாவட்டம்",
    
    # Actions
    "evacuate_immediately": "உடனடியாக வெளியேறவும்",
    "move_to_safe_location": "பாதுகாப்பான இடத்திற்கு செல்லவும்",
    "prepare_evacuation": "வெளியேற தயாராகவும்",
    "stay_alert": "விழிப்புடன் இருங்கள்",
    "monitor_updates": "புதுப்பிப்புகளை கண்காணிக்கவும்",
    
    # Infrastructure
    "river_level": "ஆற்று நீர்மட்டம்",
    "rainfall": "மழை அளவு",
    "dam": "அணை",
    "reservoir": "நீர்த்தேக்கம்",
    
    # Organizations
    "sdma": "மாநில பேரிடர் மேலாண்மை ஆணையம்",
    "ndma": "தேசிய பேரிடர் மேலாண்மை ஆணையம்",
    
    # Time-related
    "hours": "மணிநேரம்",
    "days": "நாட்கள்",
    "minutes": "நிமிடங்கள்"
}


# District names in Tamil (mapping)
DISTRICT_NAMES_TAMIL = {
    "Chennai": "சென்னை",
    "Madurai": "மதுரை",
    "Coimbatore": "கோயம்புத்தூர்",
    "Tiruchirappalli": "திருச்சிராப்பள்ளி",
    "Salem": "சேலம்",
    "Tirunelveli": "திருநெல்வேலி",
    "Tiruppur": "திருப்பூர்",
    "Erode": "ஈரோடு",
    "Vellore": "வேலூர்",
    "Thoothukudi": "தூத்துக்குடி",
    "Thanjavur": "தஞ்சாவூர்",
    "Dindigul": "திண்டுக்கல்",
    "Kanchipuram": "காஞ்சிபுரம்",
    "Cuddalore": "கடலூர்",
    "Ramanathapuram": "இராமநாதபுரம்",
    "Karur": "கரூர்",
    "Theni": "தேனி",
    "Sivaganga": "சிவகங்கை",
    "Tiruvarur": "திருவாரூர்",
    "Nagapattinam": "நாகப்பட்டினம்",
    "Ariyalur": "அரியலூர்",
    "Krishnagiri": "கிருஷ்ணகிரி",
    "Dharmapuri": "தர்மபுரி",
    "Namakkal": "நாமக்கல்",
    "Perambalur": "பெரம்பலூர்",
    "Pudukkottai": "புதுக்கோட்டை",
    "Ranipet": "ராணிப்பேட்டை",
    "Tenkasi": "தென்காசி",
    "Tirupathur": "திருப்பத்தூர்",
    "Tiruvallur": "திருவள்ளூர்",
    "Tiruvannamalai": "திருவண்ணாமலை",
    "Villupuram": "விழுப்புரம்",
    "Virudhunagar": "விருதுநகர்",
    "Kallakurichi": "கள்ளக்குறிச்சி",
    "Chengalpattu": "செங்கல்பட்டு",
    "Mayiladuthurai": "மயிலாடுதுறை",
    "The Nilgiris": "நீலகிரி"
}


def get_tamil_translation(key: str) -> str:
    """
    Get Tamil translation for a key
    
    Args:
        key: English key
    
    Returns:
        Tamil translation or original key if not found
    
    Example:
        >>> get_tamil_translation('warning')
        'எச்சரிக்கை'
    """
    return TAMIL_TRANSLATIONS.get(key.lower(), key)


def get_district_tamil_name(district_english: str) -> str:
    """
    Get Tamil name for district
    
    Args:
        district_english: District name in English
    
    Returns:
        District name in Tamil or English if not found
    
    Example:
        >>> get_district_tamil_name('Madurai')
        'மதுரை'
    """
    return DISTRICT_NAMES_TAMIL.get(district_english, district_english)


def get_action_text(alert_level, language: str = "english") -> str:
    """
    Get actionable text based on alert level
    
    Args:
        alert_level: AlertLevel enum
        language: 'english' or 'tamil'
    
    Returns:
        Action instruction text
    
    Example:
        >>> from alerts.alert_engine import AlertLevel
        >>> get_action_text(AlertLevel.WARNING, "tamil")
        'உயர்ந்த நிலப்பகுதிக்கு செல்லவும். வெள்ள பாதிப்பு பகுதிகளை தவிர்க்கவும்'
    """
    from alerts.alert_engine import AlertLevel
    
    actions_english = {
        AlertLevel.ADVISORY: "Stay informed and monitor weather updates",
        AlertLevel.WATCH: "Prepare for possible evacuation. Keep emergency kit ready",
        AlertLevel.WARNING: "Move to higher ground. Avoid flood-prone areas",
        AlertLevel.EMERGENCY: "EVACUATE IMMEDIATELY to designated safe shelters"
    }
    
    actions_tamil = {
        AlertLevel.ADVISORY: "விழிப்புடன் இருங்கள், வானிலை புதுப்பிப்புகளை கண்காணிக்கவும்",
        AlertLevel.WATCH: "வெளியேறுவதற்கு தயாராகவும். அவசர உபகரணங்களை தயார் நிலையில் வைக்கவும்",
        AlertLevel.WARNING: "உயர்ந்த நிலப்பகுதிக்கு செல்லவும். வெள்ள பாதிப்பு பகுதிகளை தவிர்க்கவும்",
        AlertLevel.EMERGENCY: "உடனடியாக நியமிக்கப்பட்ட பாதுகாப்பு முகாம்களுக்கு வெளியேறவும்"
    }
    
    if language.lower() == "tamil":
        return actions_tamil.get(alert_level, "விழிப்புடன் இருங்கள்")
    else:
        return actions_english.get(alert_level, "Stay alert")


def format_parameter_tamil(param_name: str, value: float, unit: str) -> str:
    """
    Format parameter with Tamil text
    
    Args:
        param_name: Parameter name (e.g., "rainfall")
        value: Numeric value
        unit: Unit (e.g., "mm")
    
    Returns:
        Formatted Tamil string
    
    Example:
        >>> format_parameter_tamil("rainfall", 185.5, "mm")
        'மழை அளவு: 185.5mm'
    """
    tamil_param = get_tamil_translation(param_name)
    return f"{tamil_param}: {value}{unit}"


def get_all_districts_tamil() -> Dict[str, str]:
    """
    Get complete mapping of all districts (English -> Tamil)
    
    Returns:
        Dictionary with English names as keys and Tamil names as values
    """
    return DISTRICT_NAMES_TAMIL.copy()


def get_alert_summary_tamil(alert_level: str, district_tamil: str, probability: float) -> str:
    """
    Generate short Tamil summary for alert
    
    Args:
        alert_level: Alert level string
        district_tamil: District name in Tamil
        probability: Flood probability
    
    Returns:
        Short Tamil summary string
    
    Example:
        >>> get_alert_summary_tamil("Warning", "மதுரை", 87.5)
        'எச்சரிக்கை: மதுரை வெள்ள அபாயம் 87.5%'
    """
    level_tamil = get_tamil_translation(alert_level.lower())
    return f"{level_tamil}: {district_tamil} வெள்ள அபாயம் {probability:.1f}%"


if __name__ == "__main__":
    """Test translations"""
    print("="*60)
    print("🔤 Tamil Translation Test - Floodline TN")
    print("="*60 + "\n")
    
    print("Alert Levels:")
    for level in ["advisory", "watch", "warning", "emergency"]:
        print(f"  {level.title():12s} → {get_tamil_translation(level)}")
    
    print("\nDistrict Names (Sample):")
    sample_districts = ["Chennai", "Madurai", "Coimbatore", "Salem", "Tiruchirappalli"]
    for district in sample_districts:
        print(f"  {district:20s} → {get_district_tamil_name(district)}")
    
    print("\nAction Text (Tamil):")
    from alerts.alert_engine import AlertLevel
    for level in AlertLevel:
        action = get_action_text(level, 'tamil')
        print(f"  {level.value:12s} → {action[:60]}...")
    
    print("\nAction Text (English):")
    for level in AlertLevel:
        action = get_action_text(level, 'english')
        print(f"  {level.value:12s} → {action}")
    
    print("\nParameter Formatting:")
    formatted = format_parameter_tamil("rainfall", 185.5, "mm")
    print(f"  {formatted}")
    
    print("\nAlert Summary:")
    summary = get_alert_summary_tamil("Warning", "மதுரை", 87.5)
    print(f"  {summary}")
    
    print(f"\nTotal Districts with Tamil Names: {len(DISTRICT_NAMES_TAMIL)}")
    print("\n" + "="*60)
