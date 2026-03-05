"""
Phase 5 Feature Tests - OpenRTB Bidder
Tests for:
1. Reference data endpoints (IAB categories, video placements, protocols, etc.)
2. Carrier targeting by country
3. Ad placements
4. Device and connection types
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestReferenceDataEndpoints:
    """Tests for reference data endpoints under /api/reference/*"""
    
    def test_iab_categories_returns_list(self):
        """GET /api/reference/iab-categories - Returns IAB categories with names"""
        response = requests.get(f"{BASE_URL}/api/reference/iab-categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert len(data["categories"]) > 0
        # Verify structure
        first_cat = data["categories"][0]
        assert "code" in first_cat
        assert "name" in first_cat
        # Verify known category
        iab1 = next((c for c in data["categories"] if c["code"] == "IAB1"), None)
        assert iab1 is not None
        assert iab1["name"] == "Arts & Entertainment"
        print(f"PASS: Found {len(data['categories'])} IAB categories")
    
    def test_ad_placements_returns_list(self):
        """GET /api/reference/ad-placements - Returns placement options"""
        response = requests.get(f"{BASE_URL}/api/reference/ad-placements")
        assert response.status_code == 200
        data = response.json()
        assert "placements" in data
        assert isinstance(data["placements"], list)
        assert len(data["placements"]) > 0
        # Verify structure
        first_placement = data["placements"][0]
        assert "value" in first_placement
        assert "label" in first_placement
        # Verify known placements
        placement_values = [p["value"] for p in data["placements"]]
        assert "in_app" in placement_values
        assert "in_stream" in placement_values
        assert "interstitial" in placement_values
        print(f"PASS: Found {len(data['placements'])} ad placements")
    
    def test_video_placements_returns_list(self):
        """GET /api/reference/video-placements - Returns video placement options with names"""
        response = requests.get(f"{BASE_URL}/api/reference/video-placements")
        assert response.status_code == 200
        data = response.json()
        assert "placements" in data
        assert isinstance(data["placements"], list)
        assert len(data["placements"]) > 0
        # Verify structure
        first = data["placements"][0]
        assert "id" in first
        assert "name" in first
        # Verify OpenRTB 2.5 placement types
        ids = [p["id"] for p in data["placements"]]
        assert 1 in ids  # In-Stream
        assert 2 in ids  # In-Banner
        print(f"PASS: Found {len(data['placements'])} video placements")
    
    def test_video_plcmt_returns_list(self):
        """GET /api/reference/video-plcmt - Returns OpenRTB 2.6 PLCMT types"""
        response = requests.get(f"{BASE_URL}/api/reference/video-plcmt")
        assert response.status_code == 200
        data = response.json()
        assert "plcmt" in data
        assert isinstance(data["plcmt"], list)
        assert len(data["plcmt"]) > 0
        # Verify structure
        first = data["plcmt"][0]
        assert "id" in first
        assert "name" in first
        print(f"PASS: Found {len(data['plcmt'])} video PLCMT types")
    
    def test_video_protocols_returns_list(self):
        """GET /api/reference/video-protocols - Returns VAST protocols with names"""
        response = requests.get(f"{BASE_URL}/api/reference/video-protocols")
        assert response.status_code == 200
        data = response.json()
        assert "protocols" in data
        assert isinstance(data["protocols"], list)
        assert len(data["protocols"]) > 0
        # Verify structure
        first = data["protocols"][0]
        assert "id" in first
        assert "name" in first
        # Verify VAST versions
        names = [p["name"] for p in data["protocols"]]
        vast_versions = [n for n in names if "VAST" in n]
        assert len(vast_versions) > 5  # Should have multiple VAST versions
        print(f"PASS: Found {len(data['protocols'])} video protocols including VAST 1.0-4.2")
    
    def test_video_mimes_returns_list(self):
        """GET /api/reference/video-mimes - Returns supported video MIME types"""
        response = requests.get(f"{BASE_URL}/api/reference/video-mimes")
        assert response.status_code == 200
        data = response.json()
        assert "mimes" in data
        assert isinstance(data["mimes"], list)
        assert len(data["mimes"]) > 0
        # Verify structure
        first = data["mimes"][0]
        assert "value" in first
        assert "label" in first
        # Verify common MIME types
        values = [m["value"] for m in data["mimes"]]
        assert "video/mp4" in values
        assert "video/webm" in values
        print(f"PASS: Found {len(data['mimes'])} video MIME types")
    
    def test_pod_positions_returns_list(self):
        """GET /api/reference/pod-positions - Returns ad pod position options"""
        response = requests.get(f"{BASE_URL}/api/reference/pod-positions")
        assert response.status_code == 200
        data = response.json()
        assert "positions" in data
        assert isinstance(data["positions"], list)
        assert len(data["positions"]) > 0
        # Verify structure
        first = data["positions"][0]
        assert "id" in first
        assert "name" in first
        print(f"PASS: Found {len(data['positions'])} pod positions")
    
    def test_device_types_returns_list(self):
        """GET /api/reference/device-types - Returns device type options"""
        response = requests.get(f"{BASE_URL}/api/reference/device-types")
        assert response.status_code == 200
        data = response.json()
        assert "device_types" in data
        assert isinstance(data["device_types"], list)
        assert len(data["device_types"]) > 0
        # Verify structure
        first = data["device_types"][0]
        assert "id" in first
        assert "name" in first
        # Verify known device types
        names = [d["name"] for d in data["device_types"]]
        assert any("Mobile" in n or "Phone" in n for n in names)
        assert any("Connected TV" in n or "CTV" in n for n in names)
        print(f"PASS: Found {len(data['device_types'])} device types")
    
    def test_connection_types_returns_list(self):
        """GET /api/reference/connection-types - Returns connection type options"""
        response = requests.get(f"{BASE_URL}/api/reference/connection-types")
        assert response.status_code == 200
        data = response.json()
        assert "connection_types" in data
        assert isinstance(data["connection_types"], list)
        assert len(data["connection_types"]) > 0
        # Verify structure
        first = data["connection_types"][0]
        assert "id" in first
        assert "name" in first
        # Verify known connection types
        names = [c["name"] for c in data["connection_types"]]
        assert any("WiFi" in n for n in names)
        assert any("4G" in n or "5G" in n or "Cellular" in n for n in names)
        print(f"PASS: Found {len(data['connection_types'])} connection types")


class TestCarriersByCountry:
    """Tests for carrier targeting by country"""
    
    def test_carriers_usa_returns_major_carriers(self):
        """GET /api/reference/carriers/USA - Returns US carriers (Verizon, AT&T, etc.)"""
        response = requests.get(f"{BASE_URL}/api/reference/carriers/USA")
        assert response.status_code == 200
        data = response.json()
        assert "country" in data
        assert data["country"] == "USA"
        assert "carriers" in data
        assert isinstance(data["carriers"], list)
        assert len(data["carriers"]) > 0
        # Verify structure
        first = data["carriers"][0]
        assert "name" in first
        assert "mcc" in first
        assert "mnc" in first
        # Verify known US carriers
        names = [c["name"] for c in data["carriers"]]
        assert "Verizon" in names
        assert "AT&T" in names
        assert "T-Mobile" in names
        print(f"PASS: Found {len(data['carriers'])} US carriers including Verizon, AT&T, T-Mobile")
    
    def test_carriers_gbr_returns_uk_carriers(self):
        """GET /api/reference/carriers/GBR - Returns UK carriers"""
        response = requests.get(f"{BASE_URL}/api/reference/carriers/GBR")
        assert response.status_code == 200
        data = response.json()
        assert data["country"] == "GBR"
        assert "carriers" in data
        assert len(data["carriers"]) > 0
        names = [c["name"] for c in data["carriers"]]
        assert any("EE" in n or "O2" in n or "Vodafone" in n for n in names)
        print(f"PASS: Found {len(data['carriers'])} UK carriers")
    
    def test_carriers_lowercase_country_code(self):
        """GET /api/reference/carriers/usa - Should work with lowercase country code"""
        response = requests.get(f"{BASE_URL}/api/reference/carriers/usa")
        assert response.status_code == 200
        data = response.json()
        assert data["country"] == "USA"  # Should normalize to uppercase
        print("PASS: Lowercase country code normalized correctly")
    
    def test_carriers_unknown_country_returns_empty(self):
        """GET /api/reference/carriers/XXX - Returns empty list for unknown country"""
        response = requests.get(f"{BASE_URL}/api/reference/carriers/XXX")
        assert response.status_code == 200
        data = response.json()
        assert data["country"] == "XXX"
        assert data["carriers"] == []
        print("PASS: Unknown country returns empty carriers list")
    
    def test_all_carriers_returns_all_countries(self):
        """GET /api/reference/carriers - Returns carriers for all countries"""
        response = requests.get(f"{BASE_URL}/api/reference/carriers")
        assert response.status_code == 200
        data = response.json()
        assert "carriers_by_country" in data
        assert isinstance(data["carriers_by_country"], dict)
        assert "USA" in data["carriers_by_country"]
        assert "GBR" in data["carriers_by_country"]
        print(f"PASS: Found carriers for {len(data['carriers_by_country'])} countries")


class TestSSPEndpointORTBVersion:
    """Tests for SSP Endpoint ORTB version field"""
    
    def test_create_ssp_endpoint_with_ortb_version(self):
        """Create SSP endpoint with ORTB version and verify it's returned"""
        # Create endpoint with ORTB 2.6
        create_payload = {
            "name": "TEST_SSP_ORTB26",
            "description": "Test SSP with ORTB 2.6",
            "ortb_version": "2.6"
        }
        response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=create_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["ortb_version"] == "2.6"
        endpoint_id = data["id"]
        print(f"PASS: Created SSP endpoint with ORTB 2.6")
        
        # Verify in list
        list_response = requests.get(f"{BASE_URL}/api/ssp-endpoints")
        assert list_response.status_code == 200
        endpoints = list_response.json()
        test_endpoint = next((e for e in endpoints if e["id"] == endpoint_id), None)
        assert test_endpoint is not None
        assert test_endpoint["ortb_version"] == "2.6"
        print("PASS: ORTB version visible in SSP endpoints list")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")
    
    def test_create_ssp_endpoint_defaults_to_25(self):
        """Create SSP endpoint without specifying ORTB version defaults to 2.5"""
        create_payload = {
            "name": "TEST_SSP_DEFAULT",
            "description": "Test SSP with default ORTB"
        }
        response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=create_payload)
        assert response.status_code == 200
        data = response.json()
        # Should default to 2.5
        assert data.get("ortb_version") == "2.5" or data.get("ortb_version") is None
        endpoint_id = data["id"]
        print("PASS: SSP endpoint created with default ORTB version")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")


class TestCampaignGeoTargeting:
    """Tests for campaign geo targeting with lat/long/radius"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test creative first"""
        creative_payload = {
            "name": "TEST_Creative_Geo",
            "type": "banner",
            "format": "raw_banner",
            "adomain": ["test.com"],
            "cat": ["IAB1"],
            "banner_data": {"width": 300, "height": 250}
        }
        response = requests.post(f"{BASE_URL}/api/creatives", json=creative_payload)
        self.creative_id = response.json()["id"]
        yield
        # Cleanup
        requests.delete(f"{BASE_URL}/api/creatives/{self.creative_id}")
    
    def test_create_campaign_with_geo_coordinates(self):
        """Create campaign with lat/long/radius targeting"""
        campaign_payload = {
            "name": "TEST_Geo_Campaign",
            "bid_price": 2.0,
            "creative_id": self.creative_id,
            "targeting": {
                "geo": {
                    "countries": ["USA"],
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "radius_km": 50
                }
            }
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_payload)
        assert response.status_code == 200
        data = response.json()
        campaign_id = data["id"]
        
        # Verify geo targeting was saved
        get_response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert get_response.status_code == 200
        campaign = get_response.json()
        geo = campaign.get("targeting", {}).get("geo", {})
        assert geo.get("latitude") == 34.0522
        assert geo.get("longitude") == -118.2437
        assert geo.get("radius_km") == 50
        print("PASS: Campaign created with lat/long/radius geo targeting")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")


class TestCampaignDeviceTargeting:
    """Tests for campaign device type and carrier targeting"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test creative first"""
        creative_payload = {
            "name": "TEST_Creative_Device",
            "type": "banner",
            "format": "raw_banner",
            "adomain": ["test.com"],
            "cat": ["IAB1"],
            "banner_data": {"width": 300, "height": 250}
        }
        response = requests.post(f"{BASE_URL}/api/creatives", json=creative_payload)
        self.creative_id = response.json()["id"]
        yield
        # Cleanup
        requests.delete(f"{BASE_URL}/api/creatives/{self.creative_id}")
    
    def test_create_campaign_with_device_types(self):
        """Create campaign with device type and connection type targeting"""
        campaign_payload = {
            "name": "TEST_Device_Campaign",
            "bid_price": 2.5,
            "creative_id": self.creative_id,
            "targeting": {
                "device": {
                    "device_types": [4, 5],  # Phone, Tablet
                    "connection_types": [2, 6],  # WiFi, 4G
                    "carriers": ["Verizon", "AT&T"]
                }
            }
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_payload)
        assert response.status_code == 200
        data = response.json()
        campaign_id = data["id"]
        
        # Verify targeting was saved
        get_response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert get_response.status_code == 200
        campaign = get_response.json()
        device = campaign.get("targeting", {}).get("device", {})
        assert 4 in device.get("device_types", [])
        assert 5 in device.get("device_types", [])
        assert 2 in device.get("connection_types", [])
        print("PASS: Campaign created with device type and connection type targeting")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")


class TestCampaignVideoTargeting:
    """Tests for campaign video targeting with full OpenRTB fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test video creative first"""
        creative_payload = {
            "name": "TEST_Creative_Video",
            "type": "video",
            "format": "vast_xml",
            "adomain": ["test.com"],
            "cat": ["IAB1"],
            "video_data": {"duration": 30, "width": 1920, "height": 1080}
        }
        response = requests.post(f"{BASE_URL}/api/creatives", json=creative_payload)
        self.creative_id = response.json()["id"]
        yield
        # Cleanup
        requests.delete(f"{BASE_URL}/api/creatives/{self.creative_id}")
    
    def test_create_campaign_with_full_video_targeting(self):
        """Create campaign with full video targeting (placements, plcmt, protocols, mimes)"""
        campaign_payload = {
            "name": "TEST_Video_Campaign",
            "bid_price": 5.0,
            "creative_id": self.creative_id,
            "targeting": {
                "video": {
                    "placements": [1, 2],  # In-Stream, In-Banner
                    "plcmts": [1, 2],  # OpenRTB 2.6 plcmt
                    "protocols": [2, 3, 7],  # VAST 2.0, 3.0, 4.0
                    "mimes": ["video/mp4", "video/webm"],
                    "min_duration": 5,
                    "max_duration": 60,
                    "pod_positions": [1, 2]  # First, Last
                }
            }
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_payload)
        assert response.status_code == 200
        data = response.json()
        campaign_id = data["id"]
        
        # Verify targeting was saved
        get_response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert get_response.status_code == 200
        campaign = get_response.json()
        video = campaign.get("targeting", {}).get("video", {})
        assert 1 in video.get("placements", [])
        assert 2 in video.get("plcmts", [])
        assert "video/mp4" in video.get("mimes", [])
        assert 2 in video.get("protocols", [])
        print("PASS: Campaign created with full video targeting")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")


class TestCampaignAdPlacements:
    """Tests for campaign ad placements field"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create test creative first"""
        creative_payload = {
            "name": "TEST_Creative_Placements",
            "type": "banner",
            "format": "raw_banner",
            "adomain": ["test.com"],
            "cat": ["IAB1"],
            "banner_data": {"width": 300, "height": 250}
        }
        response = requests.post(f"{BASE_URL}/api/creatives", json=creative_payload)
        self.creative_id = response.json()["id"]
        yield
        # Cleanup
        requests.delete(f"{BASE_URL}/api/creatives/{self.creative_id}")
    
    def test_create_campaign_with_ad_placements(self):
        """Create campaign with ad placements targeting"""
        campaign_payload = {
            "name": "TEST_Placements_Campaign",
            "bid_price": 2.0,
            "creative_id": self.creative_id,
            "placements": ["in_app", "in_stream", "interstitial"]
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_payload)
        assert response.status_code == 200
        data = response.json()
        campaign_id = data["id"]
        
        # Verify placements were saved
        get_response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert get_response.status_code == 200
        campaign = get_response.json()
        assert "in_app" in campaign.get("placements", [])
        assert "interstitial" in campaign.get("placements", [])
        print("PASS: Campaign created with ad placements")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")


# Run tests when executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
