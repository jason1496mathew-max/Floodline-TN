"""
Mock SMS Dispatcher for Floodline TN
=====================================

Mock SMS dispatch system for alert distribution.
In production, integrate with Twilio, AWS SNS, or Indian SMS Gateway API.

Features:
    - Multi-group SMS dispatch (officials, public)
    - SMS length validation (160 chars)
    - Dispatch logging and audit trail
    - Cost tracking (mock)
    - Delivery status simulation

Author: Floodline TN Team
Date: February 2026
"""

from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path


class SMSDispatcher:
    """
    Mock SMS dispatcher for Floodline TN
    
    In production, integrate with:
        - Twilio API
        - AWS SNS
        - Indian SMS Gateway providers (MSG91, Fast2SMS, TextLocal)
    
    Features:
        - Recipient group management
        - SMS dispatch simulation
        - Audit logging
        - Delivery tracking
    """
    
    def __init__(self, log_dir: str = 'data/alerts'):
        """
        Initialize SMS dispatcher
        
        Args:
            log_dir: Directory for SMS logs
        """
        self.log_path = Path(log_dir) / 'sms_log.json'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Mock phone numbers (in production, fetch from database)
        self.recipient_groups = {
            "officials": [
                "+91-98765-43210",  # District Collector
                "+91-98765-43211",  # SDMA Officer
                "+91-98765-43212",  # Revenue Officer
                "+91-98765-43213"   # Police Control Room
            ],
            "public": []  # Would be district-specific subscriber lists
        }
        
        # SMS cost (mock, in INR)
        self.sms_cost = 0.02  # 2 paise per SMS
    
    def dispatch_sms(
        self,
        alert: Dict,
        recipients: str = "all"  # 'officials', 'public', 'all'
    ) -> Dict:
        """
        Dispatch SMS alerts
        
        Args:
            alert: Alert dictionary from AlertEngine
            recipients: Target recipient group
        
        Returns:
            Dispatch status dictionary
        
        Example:
            >>> dispatcher = SMSDispatcher()
            >>> result = dispatcher.dispatch_sms(alert, recipients="officials")
            >>> result['status']
            'dispatched'
        """
        messages_sent = []
        
        # Determine recipients based on alert level
        if alert['alert_level'] in ['Advisory', 'Watch']:
            # Only officials for lower-level alerts
            target_groups = ['officials']
        elif alert['alert_level'] == 'Warning':
            # Officials + public for warnings
            target_groups = ['officials', 'public'] if recipients == 'all' else [recipients]
        else:  # Emergency
            # All channels for emergency
            target_groups = ['officials', 'public']
        
        # Send to officials
        if 'officials' in target_groups:
            for phone in self.recipient_groups["officials"]:
                result = self._send_single_sms(
                    phone_number=phone,
                    message=alert['messages']['sms_english'],
                    alert_id=alert['alert_id'],
                    recipient_type="official"
                )
                messages_sent.append(result)
        
        # Send to public
        if 'public' in target_groups:
            # In production, fetch subscribers for this district
            # For demo, simulate public notification
            public_count = self._get_public_subscriber_count(alert['district'])
            
            messages_sent.append({
                "recipient": "PUBLIC_GROUP",
                "recipient_type": "public",
                "district": alert['district'],
                "subscriber_count": public_count,
                "message": alert['messages']['sms_tamil'][:160],
                "status": "queued",
                "timestamp": datetime.now().isoformat(),
                "cost": self.sms_cost * public_count
            })
        
        # Log dispatch
        self._log_dispatch(alert['alert_id'], messages_sent, alert)
        
        total_cost = sum(msg.get('cost', self.sms_cost) for msg in messages_sent)
        
        return {
            "alert_id": alert['alert_id'],
            "total_sent": len(messages_sent),
            "total_recipients": sum(
                msg.get('subscriber_count', 1) for msg in messages_sent
            ),
            "messages": messages_sent,
            "status": "dispatched",
            "total_cost_inr": round(total_cost, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _send_single_sms(
        self,
        phone_number: str,
        message: str,
        alert_id: str,
        recipient_type: str = "official"
    ) -> Dict:
        """
        Mock single SMS send (in production, call SMS gateway API)
        
        Args:
            phone_number: Recipient phone number
            message: SMS message text
            alert_id: Alert ID
            recipient_type: Type of recipient
        
        Returns:
            Delivery status dictionary
        """
        # Simulate API call delay and response
        # In production:
        # response = requests.post(SMS_GATEWAY_URL, {
        #     "to": phone_number,
        #     "message": message,
        #     "sender_id": "FLDLNE"
        # })
        
        return {
            "recipient": phone_number,
            "recipient_type": recipient_type,
            "message": message[:160],  # SMS length limit
            "alert_id": alert_id,
            "status": "delivered",  # Mock status (would be from API)
            "timestamp": datetime.now().isoformat(),
            "cost": self.sms_cost,
            "gateway": "mock_gateway",
            "message_id": f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    def _get_public_subscriber_count(self, district: str) -> int:
        """
        Get number of public subscribers for district (mock)
        
        In production, query subscriber database:
            SELECT COUNT(*) FROM subscribers 
            WHERE district = ? AND opted_in = true
        
        Args:
            district: District name
        
        Returns:
            Subscriber count
        """
        # Mock subscriber counts based on district population
        mock_counts = {
            "Chennai": 5000,
            "Madurai": 3500,
            "Coimbatore": 4000,
            "Tiruchirappalli": 2800,
            "Salem": 2500,
            "Vellore": 2000,
            "Tirunelveli": 1800
        }
        
        return mock_counts.get(district, 1500)  # Default 1500 subscribers
    
    def _log_dispatch(self, alert_id: str, messages: List[Dict], alert: Dict):
        """
        Log SMS dispatch for audit trail
        
        Args:
            alert_id: Alert ID
            messages: List of sent messages
            alert: Complete alert object
        """
        log_entry = {
            "alert_id": alert_id,
            "district": alert.get('district'),
            "alert_level": alert.get('alert_level'),
            "dispatched_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "total_recipients": sum(
                msg.get('subscriber_count', 1) for msg in messages
            ),
            "messages": messages,
            "alert_metadata": {
                "probability": alert.get('flood_probability'),
                "top_driver": alert.get('top_driver', {}).get('display_name')
            }
        }
        
        # Append to log file
        logs = []
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def get_dispatch_history(
        self, 
        limit: int = 10, 
        district: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve SMS dispatch history
        
        Args:
            limit: Maximum number of entries to return
            district: Optional filter by district
        
        Returns:
            List of dispatch log entries
        
        Example:
            >>> dispatcher = SMSDispatcher()
            >>> history = dispatcher.get_dispatch_history(limit=5)
            >>> len(history) <= 5
            True
        """
        if not self.log_path.exists():
            return []
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            return []
        
        # Filter by district if specified
        if district:
            logs = [log for log in logs if log.get('district') == district]
        
        return logs[-limit:]
    
    def get_dispatch_stats(self) -> Dict:
        """
        Get SMS dispatch statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.log_path.exists():
            return {
                "total_alerts": 0,
                "total_sms_sent": 0,
                "total_cost_inr": 0,
                "by_level": {}
            }
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            return {}
        
        total_alerts = len(logs)
        total_recipients = sum(log.get('total_recipients', 0) for log in logs)
        total_cost = total_recipients * self.sms_cost
        
        # By alert level
        by_level = {}
        for log in logs:
            level = log.get('alert_level', 'Unknown')
            by_level[level] = by_level.get(level, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "total_sms_sent": total_recipients,
            "total_cost_inr": round(total_cost, 2),
            "by_level": by_level,
            "average_recipients_per_alert": round(total_recipients / total_alerts, 1) if total_alerts > 0 else 0
        }


def main():
    """
    Test SMS dispatcher
    """
    from alerts.alert_engine import AlertEngine
    
    print("="*60)
    print("📱 SMS Dispatcher Test - Floodline TN")
    print("="*60 + "\n")
    
    # Generate test alert
    engine = AlertEngine()
    alert = engine.generate_alert(
        district="Madurai",
        district_tamil="மதுரை",
        flood_probability=87.5,
        top_driver={
            "display_name": "Vaigai river level exceeds danger mark",
            "contribution_pct": 42.3
        }
    )
    
    if alert.get('status') == 'no_alert':
        print("No alert to dispatch")
        return
    
    # Dispatch SMS
    dispatcher = SMSDispatcher()
    result = dispatcher.dispatch_sms(alert, recipients="all")
    
    print(f"✅ SMS Dispatch Complete")
    print(f"   Alert ID: {result['alert_id']}")
    print(f"   Messages Sent: {result['total_sent']}")
    print(f"   Total Recipients: {result['total_recipients']}")
    print(f"   Total Cost: ₹{result['total_cost_inr']}")
    
    print(f"\n📱 Sample SMS Message (English):")
    print("-" * 60)
    print(alert['messages']['sms_english'])
    print("-" * 60)
    
    print(f"\n📱 Sample SMS Message (Tamil):")
    print("-" * 60)
    print(alert['messages']['sms_tamil'])
    print("-" * 60)
    
    # Show dispatch details
    print(f"\n📋 Dispatch Details:")
    for i, msg in enumerate(result['messages'][:3], 1):  # Show first 3
        print(f"\n   Message {i}:")
        print(f"      Recipient: {msg.get('recipient', 'N/A')}")
        print(f"      Type: {msg.get('recipient_type', 'N/A')}")
        print(f"      Status: {msg.get('status', 'N/A')}")
        if 'subscriber_count' in msg:
            print(f"      Subscribers: {msg['subscriber_count']}")
    
    # Show history
    history = dispatcher.get_dispatch_history(limit=5)
    print(f"\n📋 Recent Dispatch History ({len(history)} alerts):")
    for entry in history:
        print(f"   {entry['alert_id']:25s} | {entry['district']:15s} | "
              f"{entry['alert_level']:10s} | {entry['total_recipients']} recipients")
    
    # Show stats
    stats = dispatcher.get_dispatch_stats()
    print(f"\n📊 Dispatch Statistics:")
    print(f"   Total Alerts: {stats['total_alerts']}")
    print(f"   Total SMS Sent: {stats['total_sms_sent']}")
    print(f"   Total Cost: ₹{stats['total_cost_inr']}")
    print(f"   By Level: {stats['by_level']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
