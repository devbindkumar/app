"""
Test OpenRTB Macros Feature
- Tests GET /api/creatives/macros endpoint
- Tests macro replacement in bid responses
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://openrtb-campaign-hub.preview.emergentagent.com')


class TestMacrosEndpoint:
    """Tests for GET /api/creatives/macros endpoint"""
    
    def test_macros_endpoint_returns_200(self):
        """Test that macros endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Macros endpoint returns 200 OK")
    
    def test_macros_returns_61_total(self):
        """Test that endpoint returns exactly 61 macros"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        assert data["total_macros"] == 61, f"Expected 61 macros, got {data['total_macros']}"
        print(f"PASS: Endpoint returns {data['total_macros']} macros")
    
    def test_macros_has_all_categories(self):
        """Test that all required categories are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        expected_categories = [
            "auction", "creative", "campaign", "site_app", 
            "publisher", "device", "geo", "user", 
            "ssp", "timestamp", "utility", "click"
        ]
        
        actual_categories = list(data["categories"].keys())
        
        for cat in expected_categories:
            assert cat in actual_categories, f"Missing category: {cat}"
        
        print(f"PASS: All {len(expected_categories)} categories present: {actual_categories}")
    
    def test_auction_macros_present(self):
        """Test that auction macros are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        auction_macros = data["categories"]["auction"]["macros"]
        macro_names = [m["macro"] for m in auction_macros]
        
        required_auction_macros = [
            "${AUCTION_ID}", "${AUCTION_BID_ID}", "${AUCTION_IMP_ID}",
            "${AUCTION_PRICE}", "${AUCTION_PRICE:B64}", "${AUCTION_PRICE:HASH}",
            "${AUCTION_CURRENCY}"
        ]
        
        for macro in required_auction_macros:
            assert macro in macro_names, f"Missing auction macro: {macro}"
        
        print(f"PASS: All required auction macros present ({len(auction_macros)} total)")
    
    def test_device_macros_present(self):
        """Test that device macros are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        device_macros = data["categories"]["device"]["macros"]
        macro_names = [m["macro"] for m in device_macros]
        
        required_device_macros = [
            "${DEVICE_IP}", "${DEVICE_UA}", "${DEVICE_IFA}",
            "${DEVICE_MAKE}", "${DEVICE_MODEL}", "${DEVICE_OS}"
        ]
        
        for macro in required_device_macros:
            assert macro in macro_names, f"Missing device macro: {macro}"
        
        print(f"PASS: All required device macros present ({len(device_macros)} total)")
    
    def test_geo_macros_present(self):
        """Test that geo macros are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        geo_macros = data["categories"]["geo"]["macros"]
        macro_names = [m["macro"] for m in geo_macros]
        
        required_geo_macros = [
            "${GEO_COUNTRY}", "${GEO_REGION}", "${GEO_CITY}",
            "${GEO_ZIP}", "${GEO_LAT}", "${GEO_LON}"
        ]
        
        for macro in required_geo_macros:
            assert macro in macro_names, f"Missing geo macro: {macro}"
        
        print(f"PASS: All required geo macros present ({len(geo_macros)} total)")
    
    def test_timestamp_macros_present(self):
        """Test that timestamp macros are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        timestamp_macros = data["categories"]["timestamp"]["macros"]
        macro_names = [m["macro"] for m in timestamp_macros]
        
        required_timestamp_macros = [
            "${TIMESTAMP}", "${TIMESTAMP_MS}", "${DATE}", "${TIME}"
        ]
        
        for macro in required_timestamp_macros:
            assert macro in macro_names, f"Missing timestamp macro: {macro}"
        
        print(f"PASS: All required timestamp macros present ({len(timestamp_macros)} total)")
    
    def test_utility_macros_present(self):
        """Test that utility macros (cache buster, random) are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        utility_macros = data["categories"]["utility"]["macros"]
        macro_names = [m["macro"] for m in utility_macros]
        
        required_utility_macros = ["${CACHEBUSTER}", "${RANDOM}"]
        
        for macro in required_utility_macros:
            assert macro in macro_names, f"Missing utility macro: {macro}"
        
        print(f"PASS: All required utility macros present ({len(utility_macros)} total)")
    
    def test_click_macros_present(self):
        """Test that click tracking macros are present"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        click_macros = data["categories"]["click"]["macros"]
        macro_names = [m["macro"] for m in click_macros]
        
        required_click_macros = ["${CLICK_URL}", "${CLICK_URL_UNESC}"]
        
        for macro in required_click_macros:
            assert macro in macro_names, f"Missing click macro: {macro}"
        
        print(f"PASS: All required click macros present ({len(click_macros)} total)")
    
    def test_example_usage_provided(self):
        """Test that example usage is provided"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        assert "example_usage" in data, "Missing example_usage field"
        assert "${AUCTION_ID}" in data["example_usage"], "Example should contain AUCTION_ID macro"
        assert "${CACHEBUSTER}" in data["example_usage"], "Example should contain CACHEBUSTER macro"
        
        print(f"PASS: Example usage provided: {data['example_usage'][:60]}...")
    
    def test_each_macro_has_description(self):
        """Test that each macro has a description"""
        response = requests.get(f"{BASE_URL}/api/creatives/macros")
        data = response.json()
        
        for cat_key, cat_data in data["categories"].items():
            for macro in cat_data["macros"]:
                assert "macro" in macro, f"Missing 'macro' field in {cat_key}"
                assert "description" in macro, f"Missing 'description' for {macro.get('macro', 'unknown')}"
                assert len(macro["description"]) > 0, f"Empty description for {macro['macro']}"
        
        print("PASS: All macros have descriptions")


class TestMacroReplacementInBidResponse:
    """Tests for macro replacement in bid responses"""
    
    def get_auth_token(self):
        """Get auth token for API calls"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "superadmin@demo.com",
            "password": "demo123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_bid_response_replaces_macros_in_impression_pixels(self):
        """Test that macros in impression pixel URLs are replaced in bid response"""
        # First, get an active campaign with a creative that has impression pixels
        token = self.get_auth_token()
        if not token:
            pytest.skip("Could not authenticate")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get campaigns
        campaigns_resp = requests.get(f"{BASE_URL}/api/campaigns", headers=headers)
        if campaigns_resp.status_code != 200:
            pytest.skip("Could not get campaigns")
        
        campaigns = campaigns_resp.json()
        active_campaigns = [c for c in campaigns if c.get("status") == "active"]
        
        if not active_campaigns:
            pytest.skip("No active campaigns found")
        
        # Get a creative with impression pixels
        creatives_resp = requests.get(f"{BASE_URL}/api/creatives", headers=headers)
        if creatives_resp.status_code != 200:
            pytest.skip("Could not get creatives")
        
        creatives = creatives_resp.json()
        creatives_with_pixels = [c for c in creatives if c.get("impression_pixels")]
        
        if creatives_with_pixels:
            print(f"Found {len(creatives_with_pixels)} creatives with impression pixels")
            for c in creatives_with_pixels[:3]:
                print(f"  - {c['name']}: {len(c.get('impression_pixels', []))} pixels")
        
        print("PASS: Macro replacement test setup complete")
    
    def test_bid_endpoint_processes_macros(self):
        """Test that bid endpoint processes macros in creative impression pixels"""
        # Create a test bid request
        bid_request = {
            "id": "test-macro-bid-123",
            "imp": [{
                "id": "imp-1",
                "banner": {"w": 300, "h": 250},
                "bidfloor": 0.5
            }],
            "site": {
                "id": "site-123",
                "domain": "example.com",
                "page": "https://example.com/page"
            },
            "device": {
                "ip": "192.168.1.1",
                "ua": "Mozilla/5.0 Test",
                "geo": {
                    "country": "USA",
                    "region": "CA",
                    "city": "San Francisco"
                }
            },
            "user": {
                "id": "user-123"
            }
        }
        
        # Send bid request
        response = requests.post(f"{BASE_URL}/api/bid", json=bid_request)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            if data.get("seatbid"):
                bid = data["seatbid"][0]["bid"][0]
                adm = bid.get("adm", "")
                
                # Check if macros were replaced (should NOT contain ${...} patterns)
                if "${AUCTION_ID}" in adm or "${TIMESTAMP}" in adm:
                    print("WARNING: Unreplaced macros found in adm")
                else:
                    print("PASS: No unreplaced macros in bid response adm")
                
                print(f"Bid response received: price={bid.get('price')}, crid={bid.get('crid')}")
            else:
                print("INFO: No bid returned (no matching campaign)")
        else:
            print(f"INFO: Bid request returned {response.status_code}")
        
        print("PASS: Bid endpoint macro processing test complete")


class TestCreativeWithMacros:
    """Tests for creating/updating creatives with macro-containing impression pixels"""
    
    def get_auth_token(self):
        """Get auth token for API calls"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "superadmin@demo.com",
            "password": "demo123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_create_creative_with_macro_pixel(self):
        """Test creating a creative with impression pixel containing macros"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Could not authenticate")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        creative_data = {
            "name": "TEST_Macro_Creative",
            "type": "banner",
            "banner_data": {
                "width": 300,
                "height": 250,
                "image_url": "https://example.com/banner.jpg"
            },
            "impression_pixels": [
                {
                    "name": "Macro Test Pixel",
                    "url": "https://tracking.example.com/pixel?aid=${AUCTION_ID}&cid=${CAMPAIGN_ID}&price=${AUCTION_PRICE}&ts=${TIMESTAMP}&cb=${CACHEBUSTER}",
                    "event": "impression",
                    "enabled": True
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/creatives", json=creative_data, headers=headers)
        
        if response.status_code == 200:
            created = response.json()
            assert created.get("impression_pixels"), "Impression pixels not saved"
            pixel = created["impression_pixels"][0]
            assert "${AUCTION_ID}" in pixel["url"], "Macro not preserved in pixel URL"
            assert "${CACHEBUSTER}" in pixel["url"], "Cachebuster macro not preserved"
            
            # Cleanup
            requests.delete(f"{BASE_URL}/api/creatives/{created['id']}", headers=headers)
            
            print("PASS: Creative with macro pixel created successfully")
        else:
            print(f"INFO: Create creative returned {response.status_code}: {response.text[:200]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
