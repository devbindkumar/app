"""
Notification Preferences Service.
Centralized module for email notification preferences to avoid circular imports.
"""
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


async def get_user_email_preferences(user_id: str) -> dict:
    """Get user's email notification preferences"""
    prefs = await db.email_preferences.find_one({"user_id": user_id})
    if prefs:
        return {
            "new_user_notifications": prefs.get("new_user_notifications", True),
            "security_alerts": prefs.get("security_alerts", True),
            "budget_alerts": prefs.get("budget_alerts", True),
            "password_reset_notifications": prefs.get("password_reset_notifications", True),
            "system_announcements": prefs.get("system_announcements", True),
            "quiet_hours_enabled": prefs.get("quiet_hours_enabled", False),
            "quiet_hours_start": prefs.get("quiet_hours_start", 22),
            "quiet_hours_end": prefs.get("quiet_hours_end", 8),
            "budget_warning_threshold": prefs.get("budget_warning_threshold", 75),
            "budget_critical_threshold": prefs.get("budget_critical_threshold", 90),
        }
    return {
        "new_user_notifications": True,
        "security_alerts": True,
        "budget_alerts": True,
        "password_reset_notifications": True,
        "system_announcements": True,
        "quiet_hours_enabled": False,
        "quiet_hours_start": 22,
        "quiet_hours_end": 8,
        "budget_warning_threshold": 75,
        "budget_critical_threshold": 90,
    }


async def should_send_notification(user_id: str, notification_type: str) -> bool:
    """
    Check if a notification should be sent based on user preferences.
    notification_type: 'new_user', 'security', 'budget', 'password_reset', 'system'
    """
    prefs = await get_user_email_preferences(user_id)
    
    type_mapping = {
        "new_user": "new_user_notifications",
        "security": "security_alerts",
        "budget": "budget_alerts",
        "password_reset": "password_reset_notifications",
        "system": "system_announcements"
    }
    
    pref_key = type_mapping.get(notification_type)
    if not pref_key:
        return True  # Unknown types default to sending
    
    # Check if notification is enabled
    if not prefs.get(pref_key, True):
        return False
    
    # Check quiet hours for non-critical notifications
    if notification_type not in ["security", "password_reset"] and prefs.get("quiet_hours_enabled", False):
        current_hour = datetime.now().hour
        start = prefs.get("quiet_hours_start", 22)
        end = prefs.get("quiet_hours_end", 8)
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            if current_hour >= start or current_hour < end:
                return False
        else:
            if start <= current_hour < end:
                return False
    
    return True


async def get_budget_thresholds(user_id: str) -> tuple:
    """Get user's budget alert thresholds (warning, critical)"""
    prefs = await get_user_email_preferences(user_id)
    return (
        prefs.get("budget_warning_threshold", 75),
        prefs.get("budget_critical_threshold", 90)
    )
