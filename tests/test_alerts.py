"""
Test Suite for Alert Engine - Floodline TN
===========================================

Comprehensive tests for alert generation, translations, and SMS dispatch.

Test Coverage:
    - Alert engine initialization
    - Alert level determination
    - Alert generation (all levels)
    - Alert validation
    - Tamil translations
    - SMS dispatch
    - Dashboard formatting

Author: Floodline TN Team
Date: February 2026
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from alerts.alert_engine import AlertEngine, AlertLevel
from alerts.translations import (
    get_tamil_translation, 
    get_district_tamil_name,
    get_action_text,
    format_parameter_tamil,
    get_alert_summary_tamil
)
from alerts.sms_mock import SMSDispatcher


class TestAlertEngine:
    """Test suite for AlertEngine core functionality"""
    
    def test_alert_engine_initialization(self):
        """Test alert engine initializes correctly"""
        engine = AlertEngine()
        assert engine is not None
        assert len(engine.thresholds) == 4
        assert AlertLevel.ADVISORY in engine.thresholds
        assert AlertLevel.WATCH in engine.thresholds
        assert AlertLevel.WARNING in engine.thresholds
        assert AlertLevel.EMERGENCY in engine.thresholds
    
    def test_alert_level_determination(self):
        """Test alert level thresholds"""
        engine = AlertEngine()
        
        # Test each threshold
        assert engine.determine_alert_level(55) == AlertLevel.ADVISORY
        assert engine.determine_alert_level(50) == AlertLevel.ADVISORY
        assert engine.determine_alert_level(64) == AlertLevel.ADVISORY
        
        assert engine.determine_alert_level(70) == AlertLevel.WATCH
        assert engine.determine_alert_level(65) == AlertLevel.WATCH
        assert engine.determine_alert_level(79) == AlertLevel.WATCH
        
        assert engine.determine_alert_level(85) == AlertLevel.WARNING
        assert engine.determine_alert_level(80) == AlertLevel.WARNING
        assert engine.determine_alert_level(89) == AlertLevel.WARNING
        
        assert engine.determine_alert_level(95) == AlertLevel.EMERGENCY
        assert engine.determine_alert_level(90) == AlertLevel.EMERGENCY
        assert engine.determine_alert_level(100) == AlertLevel.EMERGENCY
        
        # Below threshold
        assert engine.determine_alert_level(30) is None
        assert engine.determine_alert_level(49) is None
    
    def test_alert_generation_advisory(self):
        """Test Advisory level alert generation"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Coimbatore",
            district_tamil="கோயம்புத்தூர்",
            flood_probability=55.0,
            top_driver={
                "display_name": "Minor rainfall",
                "contribution_pct": 35.0
            }
        )
        
        assert alert['alert_level'] == 'Advisory'
        assert alert['flood_probability'] == 55.0
        assert 'messages' in alert
        assert 'tamil' in alert['messages']
        assert 'english' in alert['messages']
        assert 'dashboard' in alert['channels']
    
    def test_alert_generation_warning(self):
        """Test Warning level alert generation"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Madurai",
            district_tamil="மதுரை",
            flood_probability=87.5,
            top_driver={
                "display_name": "7-Day Rainfall",
                "contribution_pct": 42.3
            }
        )
        
        assert 'alert_id' in alert
        assert alert['alert_level'] == 'Warning'
        assert alert['district'] == 'Madurai'
        assert alert['flood_probability'] == 87.5
        assert 'sms' in alert['channels']
        assert 'push' in alert['channels']
    
    def test_alert_generation_emergency(self):
        """Test Emergency level alert generation"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Chennai",
            district_tamil="சென்னை",
            flood_probability=95.0,
            top_driver={
                "display_name": "River flooding",
                "contribution_pct": 60.0
            }
        )
        
        assert alert['alert_level'] == 'Emergency'
        assert 'sms' in alert['channels']
        assert 'email' in alert['channels']
        assert 'push' in alert['channels']
        assert 'dashboard' in alert['channels']
    
    def test_alert_generation_below_threshold(self):
        """Test alert generation below threshold"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Salem",
            district_tamil="சேலம்",
            flood_probability=30.0,
            top_driver={
                "display_name": "Low rainfall",
                "contribution_pct": 20.0
            }
        )
        
        assert alert['status'] == 'no_alert'
        assert 'message' in alert
    
    def test_alert_validation(self):
        """Test alert validation"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Chennai",
            district_tamil="சென்னை",
            flood_probability=90.0,
            top_driver={"display_name": "River Level", "contribution_pct": 50}
        )
        
        assert engine.validate_alert(alert) is True
        
        # Test invalid alert
        invalid_alert = {"alert_id": "TEST"}
        assert engine.validate_alert(invalid_alert) is False
    
    def test_dashboard_formatting(self):
        """Test dashboard alert formatting"""
        engine = AlertEngine()
        
        alert = engine.generate_alert(
            district="Chennai",
            district_tamil="சென்னை",
            flood_probability=92.0,
            top_driver={"display_name": "River", "contribution_pct": 45}
        )
        
        dashboard_alert = engine.format_for_dashboard(alert)
        
        assert 'color' in dashboard_alert
        assert 'icon' in dashboard_alert
        assert dashboard_alert['level'] == 'Emergency'
        assert dashboard_alert['color'] == '#F44336'  # Red
        assert dashboard_alert['icon'] == '🔴'
    
    def test_alert_expiry_times(self):
        """Test alert expiry times for different levels"""
        engine = AlertEngine()
        
        from datetime import datetime
        
        # Emergency should expire in 1 hour
        alert_emergency = engine.generate_alert(
            district="Test", district_tamil="டெஸ்ட்", 
            flood_probability=95, 
            top_driver={"display_name": "Test", "contribution_pct": 40}
        )
        
        # Advisory should expire in 12 hours
        alert_advisory = engine.generate_alert(
            district="Test", district_tamil="டெஸ்ட்", 
            flood_probability=55, 
            top_driver={"display_name": "Test", "contribution_pct": 40}
        )
        
        assert 'expires_at' in alert_emergency
        assert 'expires_at' in alert_advisory


class TestTranslations:
    """Test suite for Tamil translations"""
    
    def test_tamil_translations(self):
        """Test Tamil translation function"""
        assert get_tamil_translation('warning') == 'எச்சரிக்கை'
        assert get_tamil_translation('flood_risk') == 'வெள்ள அபாயம்'
        assert get_tamil_translation('advisory') == 'ஆலோசனை'
        assert get_tamil_translation('watch') == 'கண்காணிப்பு'
        assert get_tamil_translation('emergency') == 'அவசரநிலை'
    
    def test_district_tamil_names(self):
        """Test district Tamil name translations"""
        assert get_district_tamil_name('Madurai') == 'மதுரை'
        assert get_district_tamil_name('Chennai') == 'சென்னை'
        assert get_district_tamil_name('Coimbatore') == 'கோயம்புத்தூர்'
        assert get_district_tamil_name('Salem') == 'சேலம்'
        
        # Test unknown district
        assert get_district_tamil_name('UnknownDistrict') == 'UnknownDistrict'
    
    def test_action_text_tamil(self):
        """Test action text in Tamil"""
        action = get_action_text(AlertLevel.EMERGENCY, "tamil")
        assert len(action) > 0
        assert isinstance(action, str)
        
        action = get_action_text(AlertLevel.ADVISORY, "tamil")
        assert len(action) > 0
    
    def test_action_text_english(self):
        """Test action text in English"""
        action = get_action_text(AlertLevel.EMERGENCY, "english")
        assert "EVACUATE IMMEDIATELY" in action
        
        action = get_action_text(AlertLevel.ADVISORY, "english")
        assert "Stay informed" in action
    
    def test_parameter_formatting(self):
        """Test parameter formatting with Tamil"""
        formatted = format_parameter_tamil("rainfall", 185.5, "mm")
        assert "மழை அளவு" in formatted
        assert "185.5mm" in formatted
    
    def test_alert_summary_tamil(self):
        """Test Tamil alert summary generation"""
        summary = get_alert_summary_tamil("Warning", "மதுரை", 87.5)
        assert "எச்சரிக்கை" in summary
        assert "மதுரை" in summary
        assert "87.5" in summary


class TestSMSDispatcher:
    """Test suite for SMS dispatcher"""
    
    def test_sms_dispatcher_initialization(self):
        """Test SMS dispatcher initializes correctly"""
        dispatcher = SMSDispatcher()
        assert dispatcher is not None
        assert len(dispatcher.recipient_groups['officials']) > 0
    
    def test_sms_dispatch(self):
        """Test SMS dispatcher"""
        engine = AlertEngine()
        alert = engine.generate_alert(
            district="Madurai",
            district_tamil="மதுரை",
            flood_probability=87.5,
            top_driver={"display_name": "Rainfall", "contribution_pct": 40}
        )
        
        dispatcher = SMSDispatcher()
        result = dispatcher.dispatch_sms(alert, recipients="officials")
        
        assert result['status'] == 'dispatched'
        assert result['total_sent'] > 0
        assert 'alert_id' in result
    
    def test_sms_length_limit(self):
        """Test SMS length is enforced (160 chars)"""
        engine = AlertEngine()
        alert = engine.generate_alert(
            district="Madurai",
            district_tamil="மதுரை",
            flood_probability=87.5,
            top_driver={"display_name": "Very long driver name " * 10, "contribution_pct": 40}
        )
        
        assert len(alert['messages']['sms_english']) <= 160
        assert len(alert['messages']['sms_tamil']) <= 160
    
    def test_dispatch_history(self):
        """Test dispatch history retrieval"""
        dispatcher = SMSDispatcher()
        
        # Generate and dispatch test alert
        engine = AlertEngine()
        alert = engine.generate_alert(
            district="Chennai",
            district_tamil="சென்னை",
            flood_probability=85.0,
            top_driver={"display_name": "Test", "contribution_pct": 40}
        )
        
        dispatcher.dispatch_sms(alert)
        
        history = dispatcher.get_dispatch_history(limit=5)
        assert isinstance(history, list)
        assert len(history) > 0
    
    def test_dispatch_stats(self):
        """Test dispatch statistics"""
        dispatcher = SMSDispatcher()
        stats = dispatcher.get_dispatch_stats()
        
        assert 'total_alerts' in stats
        assert 'total_sms_sent' in stats
        assert 'by_level' in stats


class TestIntegration:
    """Integration tests for complete alert flow"""
    
    def test_complete_alert_flow(self):
        """Test complete alert generation and dispatch flow"""
        engine = AlertEngine()
        dispatcher = SMSDispatcher()
        
        # Generate alert
        alert = engine.generate_alert(
            district="Madurai",
            district_tamil="மதுரை",
            flood_probability=87.5,
            top_driver={
                "display_name": "7-Day Cumulative Rainfall",
                "contribution_pct": 42.3
            },
            additional_context={
                "rainfall_mm": 185.0,
                "river_level_m": 3.2
            }
        )
        
        # Validate alert
        assert engine.validate_alert(alert) is True
        
        # Dispatch SMS
        dispatch_result = dispatcher.dispatch_sms(alert)
        assert dispatch_result['status'] == 'dispatched'
        
        # Format for dashboard
        dashboard_alert = engine.format_for_dashboard(alert)
        assert 'color' in dashboard_alert
        assert 'icon' in dashboard_alert
    
    def test_all_alert_levels(self):
        """Test generation of all alert levels"""
        engine = AlertEngine()
        
        test_cases = [
            (55, "Advisory"),
            (70, "Watch"),
            (85, "Warning"),
            (95, "Emergency")
        ]
        
        for probability, expected_level in test_cases:
            alert = engine.generate_alert(
                district="Test",
                district_tamil="டெஸ்ட்",
                flood_probability=probability,
                top_driver={"display_name": "Test", "contribution_pct": 40}
            )
            
            assert alert['alert_level'] == expected_level
            assert engine.validate_alert(alert) is True


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Running Alert Engine Tests - Floodline TN")
    print("="*60 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    main()
