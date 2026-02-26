"""
Alert Engine for Floodline TN
==============================

Multi-level alert generation engine with Tamil/English bilingual support.

Alert Levels:
    - Advisory (50-64%): Blue banner, Dashboard only
    - Watch (65-79%): Yellow banner, SMS to officials + Push
    - Warning (80-89%): Orange banner, SMS to all + Push + Email
    - Emergency (90-100%): Red banner, All channels + Dashboard takeover

Author: Floodline TN Team
Date: February 2026
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path


class AlertLevel(Enum):
    """Alert severity levels"""
    ADVISORY = "Advisory"
    WATCH = "Watch"
    WARNING = "Warning"
    EMERGENCY = "Emergency"


class AlertChannel(Enum):
    """Alert delivery channels"""
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    DASHBOARD = "dashboard"


class AlertEngine:
    """
    Multi-level alert generation engine for Floodline TN
    
    Features:
        - Threshold-based alert level determination
        - Bilingual message generation (Tamil + English)
        - Multi-channel dispatch routing
        - Alert validation and formatting
        - Dashboard integration support
    """
    
    def __init__(self):
        """Initialize alert engine with thresholds and channel mappings"""
        self.thresholds = {
            AlertLevel.ADVISORY: (50, 64),
            AlertLevel.WATCH: (65, 79),
            AlertLevel.WARNING: (80, 89),
            AlertLevel.EMERGENCY: (90, 100)
        }
        
        self.channels_by_level = {
            AlertLevel.ADVISORY: [AlertChannel.DASHBOARD],
            AlertLevel.WATCH: [AlertChannel.DASHBOARD, AlertChannel.PUSH],
            AlertLevel.WARNING: [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.DASHBOARD],
            AlertLevel.EMERGENCY: [AlertChannel.SMS, AlertChannel.EMAIL, AlertChannel.PUSH, AlertChannel.DASHBOARD]
        }
        
        self.alert_counter = 0
    
    def determine_alert_level(self, flood_probability: float) -> Optional[AlertLevel]:
        """
        Determine alert level based on flood probability
        
        Args:
            flood_probability: Flood risk probability (0-100)
        
        Returns:
            AlertLevel enum or None if below threshold
        
        Example:
            >>> engine = AlertEngine()
            >>> engine.determine_alert_level(87.5)
            <AlertLevel.WARNING: 'Warning'>
        """
        for level, (min_prob, max_prob) in self.thresholds.items():
            if min_prob <= flood_probability <= max_prob:
                return level
        
        return None  # Below advisory threshold
    
    def generate_alert(
        self,
        district: str,
        district_tamil: str,
        flood_probability: float,
        top_driver: Dict,
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate complete alert with all metadata
        
        Args:
            district: District name (English)
            district_tamil: District name (Tamil)
            flood_probability: Flood risk probability (0-100)
            top_driver: Top SHAP driver dict {display_name, contribution_pct}
            additional_context: Optional context (e.g., river levels, rainfall)
        
        Returns:
            Complete alert dictionary with messages, channels, and metadata
        
        Example:
            >>> alert = engine.generate_alert(
            ...     district="Madurai",
            ...     district_tamil="மதுரை",
            ...     flood_probability=87.5,
            ...     top_driver={"display_name": "7-Day Rainfall", "contribution_pct": 42.3}
            ... )
            >>> alert['alert_level']
            'Warning'
        """
        alert_level = self.determine_alert_level(flood_probability)
        
        if not alert_level:
            return {
                "status": "no_alert",
                "message": f"Probability {flood_probability}% below alert threshold (50%)"
            }
        
        # Generate alert ID
        self.alert_counter += 1
        alert_id = f"FLT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.alert_counter:04d}"
        
        # Get channels
        channels = self.channels_by_level[alert_level]
        
        # Generate messages
        messages = self._generate_messages(
            district, district_tamil, alert_level, 
            flood_probability, top_driver, additional_context
        )
        
        # Build alert object
        alert = {
            "alert_id": alert_id,
            "district": district,
            "district_tamil": district_tamil,
            "alert_level": alert_level.value,
            "flood_probability": round(flood_probability, 2),
            "top_driver": top_driver,
            "channels": [ch.value for ch in channels],
            "messages": messages,
            "timestamp": datetime.now().isoformat(),
            "expires_at": self._calculate_expiry(alert_level).isoformat(),
            "status": "pending",
            "metadata": {
                "system": "Floodline TN",
                "version": "1.0.0",
                "additional_context": additional_context or {}
            }
        }
        
        return alert
    
    def _generate_messages(
        self,
        district: str,
        district_tamil: str,
        alert_level: AlertLevel,
        probability: float,
        top_driver: Dict,
        additional_context: Optional[Dict]
    ) -> Dict[str, str]:
        """
        Generate Tamil and English alert messages
        
        Args:
            district: District name (English)
            district_tamil: District name (Tamil)
            alert_level: AlertLevel enum
            probability: Flood probability
            top_driver: Top risk driver
            additional_context: Additional context data
        
        Returns:
            Dictionary with tamil, english, sms_tamil, sms_english messages
        """
        from alerts.translations import get_tamil_translation, get_action_text
        
        # Get action text based on alert level
        action_english = get_action_text(alert_level, "english")
        action_tamil = get_action_text(alert_level, "tamil")
        
        # Driver text
        driver_name = top_driver.get('display_name', 'Unknown factor')
        driver_contribution = top_driver.get('contribution_pct', 0)
        
        # Tamil message
        tamil_message = (
            f"⚠️ {get_tamil_translation(alert_level.value.lower())}: "
            f"{district_tamil} மாவட்டத்தில் "
            f"{get_tamil_translation('flood_risk')} "
            f"{get_tamil_translation(self._get_risk_level_tamil(alert_level))}. "
            f"\n\n"
            f"வெள்ள நிகழ்தகவு: {probability:.1f}%\n"
            f"{get_tamil_translation('reason')}: {driver_name} "
            f"({driver_contribution:.0f}% பங்களிப்பு)\n"
            f"\n"
            f"🚨 {action_tamil}\n"
            f"\n"
            f"தொடர்புக்கு: 1070 (SDMA)\n"
            f"- Floodline TN"
        )
        
        # English message
        english_message = (
            f"⚠️ {alert_level.value.upper()} ALERT: "
            f"High flood risk in {district} district.\n"
            f"\n"
            f"Flood Probability: {probability:.1f}%\n"
            f"Primary Cause: {driver_name} ({driver_contribution:.0f}% contribution)\n"
            f"\n"
            f"🚨 {action_english}\n"
            f"\n"
            f"Contact: 1070 (State Disaster Management)\n"
            f"- Floodline TN"
        )
        
        # Short SMS version (160 chars limit)
        sms_tamil = (
            f"{get_tamil_translation(alert_level.value.lower())}: {district_tamil} வெள்ள அபாயம் "
            f"{probability:.0f}%. {action_tamil[:50]}. SDMA: 1070"
        )
        
        sms_english = (
            f"{alert_level.value.upper()}: {district} flood risk {probability:.0f}%. "
            f"{action_english[:50]}. SDMA: 1070"
        )
        
        return {
            "tamil": tamil_message,
            "english": english_message,
            "sms_tamil": sms_tamil[:160],  # Enforce SMS length limit
            "sms_english": sms_english[:160]
        }
    
    def _get_risk_level_tamil(self, alert_level: AlertLevel) -> str:
        """Get Tamil risk level descriptor"""
        mapping = {
            AlertLevel.ADVISORY: "low",
            AlertLevel.WATCH: "medium",
            AlertLevel.WARNING: "high",
            AlertLevel.EMERGENCY: "very_high"
        }
        return mapping.get(alert_level, "medium")
    
    def _calculate_expiry(self, alert_level: AlertLevel) -> datetime:
        """
        Calculate alert expiry time based on level
        
        Higher severity alerts expire faster to ensure updates
        
        Args:
            alert_level: AlertLevel enum
        
        Returns:
            Expiry datetime
        """
        expiry_hours = {
            AlertLevel.ADVISORY: 12,
            AlertLevel.WATCH: 6,
            AlertLevel.WARNING: 3,
            AlertLevel.EMERGENCY: 1
        }
        
        hours = expiry_hours[alert_level]
        return datetime.now() + timedelta(hours=hours)
    
    def validate_alert(self, alert: Dict) -> bool:
        """
        Validate alert structure before dispatch
        
        Args:
            alert: Alert dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'alert_id', 'district', 'alert_level', 
            'flood_probability', 'channels', 'messages'
        ]
        
        for field in required_fields:
            if field not in alert:
                return False
        
        # Validate messages
        if 'tamil' not in alert['messages'] or 'english' not in alert['messages']:
            return False
        
        # Validate probability range
        if not (0 <= alert['flood_probability'] <= 100):
            return False
        
        return True
    
    def format_for_dashboard(self, alert: Dict) -> Dict:
        """
        Format alert for dashboard display
        
        Args:
            alert: Complete alert dictionary
        
        Returns:
            Dashboard-formatted alert with UI metadata
        """
        level_colors = {
            "Advisory": "#2196F3",
            "Watch": "#FFC107",
            "Warning": "#FF9800",
            "Emergency": "#F44336"
        }
        
        return {
            "alert_id": alert['alert_id'],
            "district": alert['district'],
            "level": alert['alert_level'],
            "color": level_colors.get(alert['alert_level'], "#2196F3"),
            "probability": alert['flood_probability'],
            "message": alert['messages']['english'],
            "message_tamil": alert['messages']['tamil'],
            "timestamp": alert['timestamp'],
            "expires_at": alert.get('expires_at'),
            "icon": self._get_icon(alert['alert_level']),
            "top_driver": alert.get('top_driver', {}).get('display_name', 'Unknown')
        }
    
    def _get_icon(self, level: str) -> str:
        """Get emoji icon for alert level"""
        icons = {
            "Advisory": "ℹ️",
            "Watch": "⚠️",
            "Warning": "🚨",
            "Emergency": "🔴"
        }
        return icons.get(level, "⚠️")


def main():
    """
    Test alert engine
    """
    print("="*60)
    print("🔔 Alert Engine Test - Floodline TN")
    print("="*60 + "\n")
    
    engine = AlertEngine()
    
    # Test scenario: Madurai high risk
    alert = engine.generate_alert(
        district="Madurai",
        district_tamil="மதுரை",
        flood_probability=87.5,
        top_driver={
            "display_name": "7-Day Cumulative Rainfall (mm)",
            "contribution_pct": 42.3
        },
        additional_context={
            "rainfall_mm": 185.0,
            "river_level_m": 3.2,
            "vaigai_river": "Above danger mark"
        }
    )
    
    if alert.get('status') != 'no_alert':
        print(f"✅ Alert Generated: {alert['alert_id']}")
        print(f"   Level: {alert['alert_level']}")
        print(f"   Probability: {alert['flood_probability']}%")
        print(f"   Channels: {', '.join(alert['channels'])}")
        print(f"\n📱 Tamil Message:")
        print("-" * 60)
        print(alert['messages']['tamil'])
        print("\n📱 English Message:")
        print("-" * 60)
        print(alert['messages']['english'])
        
        # Validate
        is_valid = engine.validate_alert(alert)
        print(f"\n✅ Alert Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Dashboard format
        dashboard_alert = engine.format_for_dashboard(alert)
        print(f"\n📊 Dashboard Format:")
        print(json.dumps(dashboard_alert, indent=2, ensure_ascii=False))
    else:
        print(f"ℹ️ {alert['message']}")
    
    print("\n" + "="*60)
    
    # Test all levels
    print("\n🧪 Testing All Alert Levels:")
    print("="*60 + "\n")
    
    test_cases = [
        (55, "Chennai", "சென்னை"),
        (70, "Salem", "சேலம்"),
        (85, "Coimbatore", "கோயம்புத்தூர்"),
        (95, "Tiruchirappalli", "திருச்சிராப்பள்ளி")
    ]
    
    for prob, dist, dist_tamil in test_cases:
        alert = engine.generate_alert(
            district=dist,
            district_tamil=dist_tamil,
            flood_probability=prob,
            top_driver={"display_name": "Test Driver", "contribution_pct": 40}
        )
        if alert.get('status') != 'no_alert':
            print(f"{alert['alert_level']:12s} | {dist:20s} | {prob}% | {', '.join(alert['channels'])}")


if __name__ == "__main__":
    main()
