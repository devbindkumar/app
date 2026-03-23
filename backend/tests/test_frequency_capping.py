"""
Test frequency capping values persistence - Bug fix verification
Tests that Max Impressions, Period, Type, Daily Cap, and Lifetime Cap values
are correctly saved when updating a campaign via the API.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "superadmin@demo.com"
TEST_PASSWORD = "demo123"

# Test campaign ID from bug report
TEST_CAMPAIGN_ID = "e74cfdc4-ae8d-40e3-9752-fd585020b09b"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestFrequencyCapPersistence:
    """Test frequency capping values are saved correctly"""
    
    def test_get_campaign_frequency_cap(self, api_client):
        """Test that we can retrieve current frequency cap values"""
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200, f"Failed to get campaign: {response.text}"
        
        data = response.json()
        assert "frequency_cap" in data, "frequency_cap field missing from campaign"
        
        freq_cap = data["frequency_cap"]
        print(f"Current frequency_cap values: {freq_cap}")
        
        # Verify all expected fields exist
        expected_fields = ["enabled", "max_impressions", "period", "type", "daily_cap", "lifetime_cap"]
        for field in expected_fields:
            assert field in freq_cap, f"Field '{field}' missing from frequency_cap"
    
    def test_update_max_impressions(self, api_client):
        """Test that max_impressions value is saved correctly"""
        # Get current values
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        original = response.json()["frequency_cap"]
        
        # Update with new value
        new_max_impressions = 50
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": new_max_impressions,
                "period": original.get("period", "day"),
                "type": original.get("type", "user"),
                "daily_cap": original.get("daily_cap", 0),
                "lifetime_cap": original.get("lifetime_cap", 0)
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Failed to update campaign: {response.text}"
        
        # Verify the value was saved
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        updated = response.json()["frequency_cap"]
        
        assert updated["max_impressions"] == new_max_impressions, \
            f"max_impressions not saved. Expected {new_max_impressions}, got {updated['max_impressions']}"
        print(f"✓ max_impressions updated successfully: {new_max_impressions}")
    
    def test_update_period(self, api_client):
        """Test that period value is saved correctly"""
        # Test different period values
        test_periods = ["hour", "day", "week", "month", "lifetime"]
        
        for period in test_periods:
            update_payload = {
                "frequency_cap": {
                    "enabled": True,
                    "max_impressions": 25,
                    "period": period,
                    "type": "user",
                    "daily_cap": 0,
                    "lifetime_cap": 0
                }
            }
            
            response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
            assert response.status_code == 200, f"Failed to update period to '{period}': {response.text}"
            
            # Verify
            response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
            assert response.status_code == 200
            updated = response.json()["frequency_cap"]
            
            assert updated["period"] == period, \
                f"period not saved. Expected '{period}', got '{updated['period']}'"
            print(f"✓ period updated successfully: {period}")
    
    def test_update_cap_type(self, api_client):
        """Test that cap type (user/campaign) is saved correctly"""
        test_types = ["user", "campaign"]
        
        for cap_type in test_types:
            update_payload = {
                "frequency_cap": {
                    "enabled": True,
                    "max_impressions": 25,
                    "period": "day",
                    "type": cap_type,
                    "daily_cap": 0,
                    "lifetime_cap": 0
                }
            }
            
            response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
            assert response.status_code == 200, f"Failed to update type to '{cap_type}': {response.text}"
            
            # Verify
            response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
            assert response.status_code == 200
            updated = response.json()["frequency_cap"]
            
            assert updated["type"] == cap_type, \
                f"type not saved. Expected '{cap_type}', got '{updated['type']}'"
            print(f"✓ type updated successfully: {cap_type}")
    
    def test_update_daily_cap(self, api_client):
        """Test that daily_cap value is saved correctly"""
        new_daily_cap = 100
        
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": 25,
                "period": "day",
                "type": "user",
                "daily_cap": new_daily_cap,
                "lifetime_cap": 0
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Failed to update daily_cap: {response.text}"
        
        # Verify
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        updated = response.json()["frequency_cap"]
        
        assert updated["daily_cap"] == new_daily_cap, \
            f"daily_cap not saved. Expected {new_daily_cap}, got {updated['daily_cap']}"
        print(f"✓ daily_cap updated successfully: {new_daily_cap}")
    
    def test_update_lifetime_cap(self, api_client):
        """Test that lifetime_cap value is saved correctly"""
        new_lifetime_cap = 500
        
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": 25,
                "period": "day",
                "type": "user",
                "daily_cap": 100,
                "lifetime_cap": new_lifetime_cap
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Failed to update lifetime_cap: {response.text}"
        
        # Verify
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        updated = response.json()["frequency_cap"]
        
        assert updated["lifetime_cap"] == new_lifetime_cap, \
            f"lifetime_cap not saved. Expected {new_lifetime_cap}, got {updated['lifetime_cap']}"
        print(f"✓ lifetime_cap updated successfully: {new_lifetime_cap}")
    
    def test_update_all_frequency_cap_fields(self, api_client):
        """Test updating all frequency cap fields at once"""
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": 75,
                "period": "week",
                "type": "campaign",
                "daily_cap": 200,
                "lifetime_cap": 1000
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Failed to update all frequency cap fields: {response.text}"
        
        # Verify all fields
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        updated = response.json()["frequency_cap"]
        
        assert updated["enabled"] == True, "enabled not saved correctly"
        assert updated["max_impressions"] == 75, f"max_impressions not saved. Got {updated['max_impressions']}"
        assert updated["period"] == "week", f"period not saved. Got {updated['period']}"
        assert updated["type"] == "campaign", f"type not saved. Got {updated['type']}"
        assert updated["daily_cap"] == 200, f"daily_cap not saved. Got {updated['daily_cap']}"
        assert updated["lifetime_cap"] == 1000, f"lifetime_cap not saved. Got {updated['lifetime_cap']}"
        
        print("✓ All frequency cap fields updated successfully")
        print(f"  - enabled: {updated['enabled']}")
        print(f"  - max_impressions: {updated['max_impressions']}")
        print(f"  - period: {updated['period']}")
        print(f"  - type: {updated['type']}")
        print(f"  - daily_cap: {updated['daily_cap']}")
        print(f"  - lifetime_cap: {updated['lifetime_cap']}")
    
    def test_restore_original_values(self, api_client):
        """Restore original values from bug report (max_impressions=25, period=week)"""
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": 25,
                "period": "week",
                "type": "user",
                "daily_cap": 10000,
                "lifetime_cap": 10000
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Failed to restore original values: {response.text}"
        
        # Verify
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        updated = response.json()["frequency_cap"]
        
        print("✓ Original values restored:")
        print(f"  - max_impressions: {updated['max_impressions']}")
        print(f"  - period: {updated['period']}")


class TestFrequencyCapModel:
    """Test FrequencyCapConfig model accepts all field names"""
    
    def test_model_accepts_new_fields(self, api_client):
        """Test that the model accepts the new field names from frontend"""
        # These are the fields the frontend sends
        update_payload = {
            "frequency_cap": {
                "enabled": True,
                "max_impressions": 30,  # New field name
                "period": "day",         # New field name
                "type": "user",          # New field name
                "daily_cap": 50,         # New field name
                "lifetime_cap": 200      # New field name
            }
        }
        
        response = api_client.put(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}", json=update_payload)
        assert response.status_code == 200, f"Model rejected new field names: {response.text}"
        
        # Verify values were saved
        response = api_client.get(f"{BASE_URL}/api/campaigns/{TEST_CAMPAIGN_ID}")
        assert response.status_code == 200
        freq_cap = response.json()["frequency_cap"]
        
        assert freq_cap["max_impressions"] == 30
        assert freq_cap["period"] == "day"
        assert freq_cap["type"] == "user"
        assert freq_cap["daily_cap"] == 50
        assert freq_cap["lifetime_cap"] == 200
        
        print("✓ Model correctly accepts new field names from frontend")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
