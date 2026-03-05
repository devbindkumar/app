"""
Phase 7 Testing: SSP Endpoints and SSP-specific Bid Routing
Tests for:
1. SSP Endpoints page functionality
2. SSP-specific bid endpoint /api/bid/{ssp_name}
3. Generic bid endpoint /api/bid
4. Invalid SSP name returns 404
5. Campaign Comparison API
6. Bid Stream API
7. A/B Testing API
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSSPEndpointsAPI:
    """Tests for SSP Endpoint management APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_prefix = f"TEST_PHASE7_{uuid.uuid4().hex[:8]}"
    
    def test_get_ssp_endpoints(self):
        """GET /api/ssp-endpoints - should return list of SSP endpoints"""
        response = requests.get(f"{BASE_URL}/api/ssp-endpoints")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"GET /api/ssp-endpoints: {response.status_code}, {len(data)} endpoints")
    
    def test_create_ssp_endpoint(self):
        """POST /api/ssp-endpoints - should create a new SSP endpoint"""
        payload = {
            "name": f"Test SSP {uuid.uuid4().hex[:6]}",
            "description": "Test SSP for phase 7 testing",
            "ortb_version": "2.5"
        }
        response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        assert "status" in data
        print(f"POST /api/ssp-endpoints: {response.status_code}, created endpoint {data.get('id')}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{data['id']}")
    
    def test_delete_ssp_endpoint(self):
        """DELETE /api/ssp-endpoints/{endpoint_id} - should delete an SSP endpoint"""
        # Create endpoint first
        payload = {
            "name": f"Delete Test SSP {uuid.uuid4().hex[:6]}",
            "description": "To be deleted"
        }
        create_response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert create_response.status_code == 200
        endpoint_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")
        assert delete_response.status_code == 200
        print(f"DELETE /api/ssp-endpoints/{endpoint_id}: {delete_response.status_code}")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/ssp-endpoints")
        endpoints = get_response.json()
        assert not any(e.get("id") == endpoint_id for e in endpoints)
    
    def test_update_ssp_status(self):
        """PUT /api/ssp-endpoints/{endpoint_id}/status - should update endpoint status"""
        # Create endpoint first
        payload = {
            "name": f"Status Test SSP {uuid.uuid4().hex[:6]}",
            "description": "To test status update"
        }
        create_response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert create_response.status_code == 200
        endpoint_id = create_response.json()["id"]
        
        # Update status to inactive
        status_response = requests.put(
            f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}/status",
            params={"status": "inactive"}
        )
        assert status_response.status_code == 200
        print(f"PUT /api/ssp-endpoints/{endpoint_id}/status: {status_response.status_code}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")


class TestSSPSpecificBidEndpoint:
    """Tests for SSP-specific bid endpoint /api/bid/{ssp_name}"""
    
    def test_bid_endpoint_with_valid_ssp_name(self):
        """POST /api/bid/{ssp_name} - should work with valid SSP name"""
        # First create an SSP endpoint to test with
        # Note: SSP name with spaces is stored, URL uses hyphens which are converted to spaces for matching
        ssp_id = uuid.uuid4().hex[:6]
        ssp_name = f"Test SSP {ssp_id}"  # Name with spaces
        ssp_url_name = f"test-ssp-{ssp_id}"  # URL-friendly version with hyphens
        payload = {
            "name": ssp_name,
            "description": "Test SSP for bid routing",
            "ortb_version": "2.5"
        }
        create_response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert create_response.status_code == 200
        endpoint_id = create_response.json()["id"]
        
        # Activate the endpoint
        requests.put(
            f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}/status",
            params={"status": "active"}
        )
        
        # Now test the SSP-specific bid endpoint
        bid_request = {
            "id": str(uuid.uuid4()),
            "imp": [{
                "id": "1",
                "banner": {"w": 300, "h": 250}
            }],
            "site": {
                "domain": "example.com",
                "page": "https://example.com/test"
            },
            "device": {
                "devicetype": 2,
                "geo": {"country": "USA"}
            }
        }
        
        bid_response = requests.post(
            f"{BASE_URL}/api/bid/{ssp_url_name}",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 200 (bid) or 204 (no bid)
        assert bid_response.status_code in [200, 204]
        print(f"POST /api/bid/{ssp_url_name}: {bid_response.status_code}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")
    
    def test_bid_endpoint_with_invalid_ssp_name(self):
        """POST /api/bid/{ssp_name} - should return 404 for invalid SSP name"""
        invalid_ssp_name = "non-existent-ssp-12345"
        
        bid_request = {
            "id": str(uuid.uuid4()),
            "imp": [{"id": "1", "banner": {"w": 300, "h": 250}}]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid/{invalid_ssp_name}",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("detail", "").lower()
        print(f"POST /api/bid/{invalid_ssp_name}: {response.status_code} (expected 404)")
    
    def test_bid_endpoint_with_inactive_ssp(self):
        """POST /api/bid/{ssp_name} - should return 403 for inactive SSP"""
        ssp_id = uuid.uuid4().hex[:6]
        ssp_name = f"Inactive SSP {ssp_id}"  # Name with spaces
        ssp_url_name = f"inactive-ssp-{ssp_id}"  # URL-friendly version
        payload = {
            "name": ssp_name,
            "description": "Inactive SSP",
            "ortb_version": "2.5"
        }
        create_response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert create_response.status_code == 200
        endpoint_id = create_response.json()["id"]
        
        # Set to inactive
        requests.put(
            f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}/status",
            params={"status": "inactive"}
        )
        
        # Try to bid
        bid_request = {
            "id": str(uuid.uuid4()),
            "imp": [{"id": "1", "banner": {"w": 300, "h": 250}}]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid/{ssp_url_name}",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 403
        print(f"POST /api/bid/{ssp_url_name} (inactive): {response.status_code} (expected 403)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")


class TestGenericBidEndpoint:
    """Tests for generic bid endpoint /api/bid"""
    
    def test_generic_bid_endpoint_without_auth(self):
        """POST /api/bid - should work without X-API-Key authentication"""
        bid_request = {
            "id": str(uuid.uuid4()),
            "imp": [{
                "id": "1",
                "banner": {"w": 300, "h": 250, "pos": 1},
                "bidfloor": 0.5
            }],
            "site": {
                "domain": "news-site.com",
                "page": "https://news-site.com/article"
            },
            "device": {
                "devicetype": 2,
                "os": "Windows",
                "geo": {"country": "USA"}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 200 (bid) or 204 (no bid), not 401
        assert response.status_code in [200, 204]
        assert response.status_code != 401  # No authentication required
        print(f"POST /api/bid (no auth): {response.status_code}")
    
    def test_generic_bid_endpoint_with_video_request(self):
        """POST /api/bid - should handle video bid requests"""
        bid_request = {
            "id": str(uuid.uuid4()),
            "imp": [{
                "id": "1",
                "video": {
                    "w": 1920,
                    "h": 1080,
                    "mimes": ["video/mp4"],
                    "protocols": [2, 3, 5, 6],
                    "minduration": 5,
                    "maxduration": 30,
                    "placement": 1
                },
                "bidfloor": 2.0
            }],
            "site": {
                "domain": "video-site.com"
            },
            "device": {
                "devicetype": 3,
                "geo": {"country": "USA"}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [200, 204]
        print(f"POST /api/bid (video): {response.status_code}")


class TestCampaignComparisonAPI:
    """Tests for Campaign Comparison API"""
    
    def test_compare_campaigns(self):
        """POST /api/campaigns/compare - should compare 2+ campaigns"""
        # Get existing campaigns
        campaigns_response = requests.get(f"{BASE_URL}/api/campaigns")
        assert campaigns_response.status_code == 200
        campaigns = campaigns_response.json()
        
        if len(campaigns) < 2:
            pytest.skip("Need at least 2 campaigns for comparison")
        
        campaign_ids = [c["id"] for c in campaigns[:2]]
        
        response = requests.post(
            f"{BASE_URL}/api/campaigns/compare",
            json={"campaign_ids": campaign_ids}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert "metrics_comparison" in data
        print(f"POST /api/campaigns/compare: {response.status_code}")


class TestBidStreamAPI:
    """Tests for Bid Stream API"""
    
    def test_get_bid_stream(self):
        """GET /api/bid-stream - should return recent bid activity"""
        response = requests.get(f"{BASE_URL}/api/bid-stream", params={"limit": 10})
        assert response.status_code == 200
        
        data = response.json()
        assert "bids" in data
        assert "total_in_memory" in data
        assert isinstance(data["bids"], list)
        print(f"GET /api/bid-stream: {response.status_code}, {len(data.get('bids', []))} bids")


class TestABTestingAPI:
    """Tests for A/B Testing API"""
    
    def test_get_ab_tests(self):
        """GET /api/ab-tests - should return list of A/B tests"""
        response = requests.get(f"{BASE_URL}/api/ab-tests")
        assert response.status_code == 200
        
        data = response.json()
        assert "tests" in data
        assert isinstance(data["tests"], list)
        print(f"GET /api/ab-tests: {response.status_code}, {len(data.get('tests', []))} tests")
    
    def test_create_ab_test(self):
        """POST /api/ab-tests - should create new A/B test"""
        # Get existing campaigns
        campaigns_response = requests.get(f"{BASE_URL}/api/campaigns")
        campaigns = campaigns_response.json()
        
        if len(campaigns) < 2:
            pytest.skip("Need at least 2 campaigns for A/B test")
        
        campaign_ids = [c["id"] for c in campaigns[:2]]
        
        payload = {
            "name": f"Test AB {uuid.uuid4().hex[:6]}",
            "campaign_ids": campaign_ids,
            "traffic_split": [50, 50]
        }
        
        response = requests.post(f"{BASE_URL}/api/ab-tests", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        print(f"POST /api/ab-tests: {response.status_code}, test id: {data.get('id')}")


class TestEndpointURLGeneration:
    """Tests for SSP endpoint URL generation"""
    
    def test_get_ssp_endpoint_url(self):
        """GET /api/ssp-endpoints/{endpoint_id}/endpoint-url - should return unique URL"""
        # Create an SSP endpoint
        ssp_name = f"url-test-ssp-{uuid.uuid4().hex[:6]}"
        payload = {
            "name": ssp_name,
            "description": "Test endpoint URL generation"
        }
        create_response = requests.post(f"{BASE_URL}/api/ssp-endpoints", json=payload)
        assert create_response.status_code == 200
        endpoint_id = create_response.json()["id"]
        
        # Get the endpoint URL
        url_response = requests.get(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}/endpoint-url")
        assert url_response.status_code == 200
        
        data = url_response.json()
        assert "endpoint_url" in data
        assert "generic_url" in data
        assert "ssp_name" in data
        
        # Verify the URL format
        assert f"/api/bid/{ssp_name}" in data["endpoint_url"].lower()
        print(f"GET /api/ssp-endpoints/{endpoint_id}/endpoint-url: {url_response.status_code}")
        print(f"  endpoint_url: {data['endpoint_url']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
