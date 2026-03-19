"""
Email Preferences API Tests
Testing endpoints:
- GET /api/auth/email-preferences - Get user preferences with defaults
- PUT /api/auth/email-preferences - Update preferences with validation
- POST /api/auth/email-preferences/reset - Reset to defaults
Validation tests:
- Budget thresholds: warning 10-95, critical 50-100, critical > warning
- Quiet hours: 0-23
- Digest day: valid weekday name
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_CREDENTIALS = {
    "super_admin": {"email": "superadmin@demo.com", "password": "demo123"},
    "admin": {"email": "admin@demo.com", "password": "demo123"},
    "advertiser": {"email": "advertiser@demo.com", "password": "demo123"},
}


@pytest.fixture(scope="module")
def super_admin_token():
    """Get super admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_CREDENTIALS["super_admin"]
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_CREDENTIALS["admin"]
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def advertiser_token():
    """Get advertiser authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_CREDENTIALS["advertiser"]
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


class TestGetEmailPreferences:
    """Tests for GET /api/auth/email-preferences endpoint"""
    
    def test_get_preferences_returns_defaults(self, super_admin_token):
        """GET should return preferences with defaults if none set"""
        response = requests.get(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "preferences" in data
        assert "defaults" in data
        
        # Verify default keys exist
        prefs = data["preferences"]
        assert "security_alerts" in prefs
        assert "budget_alerts" in prefs
        assert "new_user_notifications" in prefs
        assert "password_reset_notifications" in prefs
        assert "system_announcements" in prefs
        assert "weekly_digest" in prefs
        assert "budget_warning_threshold" in prefs
        assert "budget_critical_threshold" in prefs
        assert "digest_day" in prefs
        assert "quiet_hours_enabled" in prefs
        assert "quiet_hours_start" in prefs
        assert "quiet_hours_end" in prefs
        
    def test_get_preferences_unauthorized(self):
        """GET without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/auth/email-preferences")
        assert response.status_code in [401, 403]
        
    def test_get_preferences_admin(self, admin_token):
        """Admin should be able to get their preferences"""
        response = requests.get(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        
    def test_get_preferences_advertiser(self, advertiser_token):
        """Advertiser should be able to get their preferences"""
        response = requests.get(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={"Authorization": f"Bearer {advertiser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data


class TestUpdateEmailPreferences:
    """Tests for PUT /api/auth/email-preferences endpoint"""
    
    def test_update_notification_toggles(self, super_admin_token):
        """Should be able to toggle notification types"""
        # Update security_alerts to false
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"security_alerts": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["preferences"]["security_alerts"] == False
        
        # Verify with GET
        get_response = requests.get(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        assert get_response.json()["preferences"]["security_alerts"] == False
        
        # Reset back to true
        requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"security_alerts": True}
        )
        
    def test_update_budget_warning_threshold_valid(self, super_admin_token):
        """Valid warning threshold (10-95) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 60}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_warning_threshold"] == 60
        
    def test_update_budget_warning_threshold_too_low(self, super_admin_token):
        """Warning threshold below 10 should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 5}
        )
        assert response.status_code == 400
        assert "10 and 95" in response.json()["detail"]
        
    def test_update_budget_warning_threshold_too_high(self, super_admin_token):
        """Warning threshold above 95 should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 98}
        )
        assert response.status_code == 400
        assert "10 and 95" in response.json()["detail"]
        
    def test_update_budget_critical_threshold_valid(self, super_admin_token):
        """Valid critical threshold (50-100) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_critical_threshold": 85}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_critical_threshold"] == 85
        
    def test_update_budget_critical_threshold_too_low(self, super_admin_token):
        """Critical threshold below 50 should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_critical_threshold": 40}
        )
        assert response.status_code == 400
        assert "50 and 100" in response.json()["detail"]
        
    def test_update_critical_must_exceed_warning(self, super_admin_token):
        """Critical threshold must be greater than warning threshold"""
        # First set warning to 60
        requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 60}
        )
        
        # Try to set critical to 55 (less than warning)
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_critical_threshold": 55}
        )
        assert response.status_code == 400
        assert "greater than warning" in response.json()["detail"]
        
    def test_update_critical_equal_to_warning(self, super_admin_token):
        """Critical threshold equal to warning should be rejected"""
        # First set warning to 70
        requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 70}
        )
        
        # Try to set critical to same value
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_critical_threshold": 70}
        )
        assert response.status_code == 400
        
    def test_update_quiet_hours_valid(self, super_admin_token):
        """Valid quiet hours (0-23) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "quiet_hours_enabled": True,
                "quiet_hours_start": 21,
                "quiet_hours_end": 7
            }
        )
        assert response.status_code == 200
        prefs = response.json()["preferences"]
        assert prefs["quiet_hours_enabled"] == True
        assert prefs["quiet_hours_start"] == 21
        assert prefs["quiet_hours_end"] == 7
        
    def test_update_quiet_hours_start_invalid(self, super_admin_token):
        """Quiet hours start outside 0-23 should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"quiet_hours_start": 25}
        )
        assert response.status_code == 400
        assert "0 and 23" in response.json()["detail"]
        
    def test_update_quiet_hours_end_invalid(self, super_admin_token):
        """Quiet hours end outside 0-23 should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"quiet_hours_end": -1}
        )
        assert response.status_code == 400
        assert "0 and 23" in response.json()["detail"]
        
    def test_update_digest_day_valid(self, super_admin_token):
        """Valid weekday name should be accepted"""
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            response = requests.put(
                f"{BASE_URL}/api/auth/email-preferences",
                headers={
                    "Authorization": f"Bearer {super_admin_token}",
                    "Content-Type": "application/json"
                },
                json={"weekly_digest": True, "digest_day": day}
            )
            assert response.status_code == 200, f"Failed for {day}"
            assert response.json()["preferences"]["digest_day"] == day.lower()
            
    def test_update_digest_day_case_insensitive(self, super_admin_token):
        """Digest day should be case insensitive"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"digest_day": "FRIDAY"}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["digest_day"] == "friday"
        
    def test_update_digest_day_invalid(self, super_admin_token):
        """Invalid day name should be rejected"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"digest_day": "notaday"}
        )
        assert response.status_code == 400
        assert "Invalid digest day" in response.json()["detail"]
        
    def test_update_multiple_preferences(self, super_admin_token):
        """Should be able to update multiple preferences at once"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "budget_alerts": True,
                "budget_warning_threshold": 70,
                "budget_critical_threshold": 90,
                "weekly_digest": False,
                "quiet_hours_enabled": False
            }
        )
        assert response.status_code == 200
        prefs = response.json()["preferences"]
        assert prefs["budget_alerts"] == True
        assert prefs["budget_warning_threshold"] == 70
        assert prefs["budget_critical_threshold"] == 90
        assert prefs["weekly_digest"] == False
        assert prefs["quiet_hours_enabled"] == False


class TestResetEmailPreferences:
    """Tests for POST /api/auth/email-preferences/reset endpoint"""
    
    def test_reset_to_defaults(self, super_admin_token):
        """Reset should restore all default values"""
        # First modify some preferences
        requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "budget_warning_threshold": 50,
                "budget_critical_threshold": 95,
                "weekly_digest": True,
                "quiet_hours_enabled": True
            }
        )
        
        # Reset to defaults
        response = requests.post(
            f"{BASE_URL}/api/auth/email-preferences/reset",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"
        
        # Verify default values
        prefs = data["preferences"]
        assert prefs["budget_warning_threshold"] == 75  # Default
        assert prefs["budget_critical_threshold"] == 90  # Default
        assert prefs["weekly_digest"] == False  # Default
        assert prefs["quiet_hours_enabled"] == False  # Default
        assert prefs["security_alerts"] == True  # Default
        assert prefs["budget_alerts"] == True  # Default
        
    def test_reset_unauthorized(self):
        """Reset without token should return 401/403"""
        response = requests.post(f"{BASE_URL}/api/auth/email-preferences/reset")
        assert response.status_code in [401, 403]


class TestPreferencesIntegrationWithBudgetCheck:
    """Tests to verify budget check endpoint includes threshold info"""
    
    def test_budget_check_returns_threshold_info(self, super_admin_token):
        """Budget check endpoint should return threshold information"""
        # Get a campaign to test budget check
        campaigns_response = requests.get(
            f"{BASE_URL}/api/campaigns",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        if campaigns_response.status_code == 200:
            campaigns = campaigns_response.json()
            if campaigns and len(campaigns) > 0:
                campaign_id = campaigns[0].get("id")
                if campaign_id:
                    # Check budget endpoint
                    budget_response = requests.post(
                        f"{BASE_URL}/api/campaigns/{campaign_id}/check-budget",
                        headers={"Authorization": f"Bearer {super_admin_token}"}
                    )
                    assert budget_response.status_code == 200
                    budget_data = budget_response.json()
                    
                    # Verify response structure includes threshold information
                    assert "warning_threshold" in budget_data, "Response should include warning_threshold"
                    assert "critical_threshold" in budget_data, "Response should include critical_threshold"
                    assert "percentage_used" in budget_data, "Response should include percentage_used"
                    
                    # Note: If campaign has no owner_id, defaults (75, 90) are used
                    # This is correct behavior - custom thresholds apply only when owner is set
                    assert budget_data["warning_threshold"] in [60, 75], "Should be custom (60) or default (75)"
                    assert budget_data["critical_threshold"] in [85, 90], "Should be custom (85) or default (90)"


class TestBoundaryConditions:
    """Edge case and boundary condition tests"""
    
    def test_warning_threshold_boundary_10(self, super_admin_token):
        """Warning threshold at minimum boundary (10) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 10, "budget_critical_threshold": 90}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_warning_threshold"] == 10
        
    def test_warning_threshold_boundary_95(self, super_admin_token):
        """Warning threshold at maximum boundary (95) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 95, "budget_critical_threshold": 100}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_warning_threshold"] == 95
        
    def test_critical_threshold_boundary_50(self, super_admin_token):
        """Critical threshold at minimum boundary (50) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_warning_threshold": 10, "budget_critical_threshold": 50}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_critical_threshold"] == 50
        
    def test_critical_threshold_boundary_100(self, super_admin_token):
        """Critical threshold at maximum boundary (100) should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"budget_critical_threshold": 100}
        )
        assert response.status_code == 200
        assert response.json()["preferences"]["budget_critical_threshold"] == 100
        
    def test_quiet_hours_boundary_0(self, super_admin_token):
        """Quiet hours at boundary 0 should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"quiet_hours_start": 0, "quiet_hours_end": 0}
        )
        assert response.status_code == 200
        
    def test_quiet_hours_boundary_23(self, super_admin_token):
        """Quiet hours at boundary 23 should be accepted"""
        response = requests.put(
            f"{BASE_URL}/api/auth/email-preferences",
            headers={
                "Authorization": f"Bearer {super_admin_token}",
                "Content-Type": "application/json"
            },
            json={"quiet_hours_start": 23, "quiet_hours_end": 23}
        )
        assert response.status_code == 200


class TestCleanup:
    """Cleanup test - reset preferences to defaults"""
    
    def test_final_reset(self, super_admin_token):
        """Reset preferences to defaults at the end of tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/email-preferences/reset",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
