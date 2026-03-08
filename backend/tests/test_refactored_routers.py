"""
Test suite for refactored server.py routers
Tests all endpoints after server.py was split into modular routers under /app/backend/routers/
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==================== HEALTH & DASHBOARD TESTS ====================

class TestHealthEndpoints:
    """Health check and basic endpoint tests"""
    
    def test_health_check(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health check endpoint working")
    
    def test_root_endpoint(self):
        """Test root endpoint - frontend or API"""
        response = requests.get(f"{BASE_URL}/")
        # Root may return HTML (frontend) or JSON (API)
        assert response.status_code == 200
        print("PASS: Root endpoint working")


class TestDashboardEndpoints:
    """Dashboard stats endpoint tests"""
    
    def test_dashboard_stats(self):
        """Test /api/dashboard/stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields
        assert "total_campaigns" in data
        assert "active_campaigns" in data
        assert "total_creatives" in data
        assert "total_bids" in data
        assert "total_wins" in data
        assert "total_impressions" in data
        assert "total_spend" in data
        
        # Verify data types
        assert isinstance(data["total_campaigns"], int)
        assert isinstance(data["total_spend"], (int, float))
        print(f"PASS: Dashboard stats - {data['total_campaigns']} campaigns, {data['total_creatives']} creatives")
    
    def test_dashboard_chart_data(self):
        """Test /api/dashboard/chart-data endpoint"""
        response = requests.get(f"{BASE_URL}/api/dashboard/chart-data")
        assert response.status_code == 200
        data = response.json()
        
        assert "labels" in data
        assert "bids" in data
        assert "wins" in data
        assert "spend" in data
        print("PASS: Dashboard chart data endpoint working")


# ==================== CAMPAIGNS CRUD TESTS ====================

class TestCampaignsEndpoints:
    """Campaign CRUD endpoint tests"""
    
    def test_get_all_campaigns(self):
        """Test GET /api/campaigns endpoint"""
        response = requests.get(f"{BASE_URL}/api/campaigns")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # Should have campaigns in DB
        
        # Verify campaign structure
        if data:
            campaign = data[0]
            assert "id" in campaign
            assert "name" in campaign
            assert "status" in campaign
            assert "bid_price" in campaign
        print(f"PASS: Get campaigns - {len(data)} campaigns returned")
    
    def test_get_campaigns_by_status(self):
        """Test GET /api/campaigns with status filter"""
        response = requests.get(f"{BASE_URL}/api/campaigns?status=active")
        assert response.status_code == 200
        data = response.json()
        
        # All returned campaigns should be active
        for campaign in data:
            assert campaign["status"] == "active"
        print(f"PASS: Get active campaigns - {len(data)} active campaigns")
    
    def test_get_single_campaign(self):
        """Test GET /api/campaigns/{id} endpoint"""
        # First get a campaign ID
        campaigns = requests.get(f"{BASE_URL}/api/campaigns").json()
        if not campaigns:
            pytest.skip("No campaigns available for testing")
        
        campaign_id = campaigns[0]["id"]
        response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == campaign_id
        print(f"PASS: Get single campaign - {data['name']}")
    
    def test_get_nonexistent_campaign(self):
        """Test GET /api/campaigns/{id} with invalid ID"""
        response = requests.get(f"{BASE_URL}/api/campaigns/nonexistent-id-12345")
        assert response.status_code == 404
        print("PASS: Get nonexistent campaign returns 404")


# ==================== CREATIVES CRUD TESTS ====================

class TestCreativesEndpoints:
    """Creative CRUD endpoint tests"""
    
    def test_get_all_creatives(self):
        """Test GET /api/creatives endpoint"""
        response = requests.get(f"{BASE_URL}/api/creatives")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # Should have creatives in DB
        
        # Verify creative structure
        if data:
            creative = data[0]
            assert "id" in creative
            assert "name" in creative
            assert "type" in creative
            assert "status" in creative
        print(f"PASS: Get creatives - {len(data)} creatives returned")
    
    def test_get_single_creative(self):
        """Test GET /api/creatives/{id} endpoint"""
        creatives = requests.get(f"{BASE_URL}/api/creatives").json()
        if not creatives:
            pytest.skip("No creatives available for testing")
        
        creative_id = creatives[0]["id"]
        response = requests.get(f"{BASE_URL}/api/creatives/{creative_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == creative_id
        print(f"PASS: Get single creative - {data['name']}")


# ==================== SSP ENDPOINTS TESTS ====================

class TestSSPEndpoints:
    """SSP endpoint management tests"""
    
    def test_get_all_ssp_endpoints(self):
        """Test GET /api/ssp-endpoints endpoint"""
        response = requests.get(f"{BASE_URL}/api/ssp-endpoints")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            endpoint = data[0]
            assert "id" in endpoint
            assert "name" in endpoint
            assert "endpoint_token" in endpoint
            assert "status" in endpoint
            assert "ortb_version" in endpoint
        print(f"PASS: Get SSP endpoints - {len(data)} endpoints returned")
    
    def test_get_ssp_endpoint_url(self):
        """Test GET /api/ssp-endpoints/{id}/endpoint-url"""
        endpoints = requests.get(f"{BASE_URL}/api/ssp-endpoints").json()
        if not endpoints:
            pytest.skip("No SSP endpoints available for testing")
        
        endpoint_id = endpoints[0]["id"]
        response = requests.get(f"{BASE_URL}/api/ssp-endpoints/{endpoint_id}/endpoint-url")
        assert response.status_code == 200
        
        data = response.json()
        assert "endpoint_url" in data
        assert "endpoint_token" in data
        assert "ortb_version" in data
        print(f"PASS: Get SSP endpoint URL - {data['endpoint_url']}")


# ==================== BID ENDPOINT TESTS ====================

class TestBidEndpoints:
    """OpenRTB bid endpoint tests"""
    
    def test_bid_with_token(self):
        """Test POST /api/bid/{token} endpoint"""
        # Get an SSP endpoint token
        endpoints = requests.get(f"{BASE_URL}/api/ssp-endpoints").json()
        if not endpoints:
            pytest.skip("No SSP endpoints available for testing")
        
        # Find active endpoint
        active_endpoint = next((e for e in endpoints if e["status"] == "active"), None)
        if not active_endpoint:
            pytest.skip("No active SSP endpoint available")
        
        token = active_endpoint["endpoint_token"]
        
        # Send bid request
        bid_request = {
            "id": "test-bid-refactor-123",
            "imp": [{
                "id": "imp1",
                "banner": {"w": 300, "h": 250},
                "bidfloor": 0.5
            }],
            "site": {"domain": "test.com"},
            "device": {"ip": "8.8.8.8", "geo": {"country": "USA"}}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid/{token}",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 200 (bid) or 204 (no-bid)
        assert response.status_code in [200, 204]
        print(f"PASS: Bid endpoint with token - status {response.status_code}")
    
    def test_bid_generic_endpoint(self):
        """Test POST /api/bid endpoint (generic)"""
        bid_request = {
            "id": "test-bid-generic-123",
            "imp": [{
                "id": "imp1",
                "banner": {"w": 300, "h": 250},
                "bidfloor": 0.1
            }],
            "site": {"domain": "test.com"},
            "device": {"ip": "8.8.8.8", "geo": {"country": "USA"}}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/bid",
            json=bid_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 200 (bid) or 204 (no-bid)
        assert response.status_code in [200, 204]
        print(f"PASS: Generic bid endpoint - status {response.status_code}")
    
    def test_bid_invalid_token(self):
        """Test POST /api/bid/{token} with invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/bid/invalid-token-xyz",
            json={"id": "test", "imp": []},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404
        print("PASS: Invalid token returns 404")


# ==================== SSP ANALYTICS TESTS ====================

class TestSSPAnalyticsEndpoints:
    """SSP Analytics endpoint tests"""
    
    def test_ssp_analytics_overview(self):
        """Test GET /api/ssp-analytics/overview endpoint"""
        response = requests.get(f"{BASE_URL}/api/ssp-analytics/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "overview" in data
        assert "ssp_rankings" in data
        assert "top_performers" in data
        
        overview = data["overview"]
        assert "total_ssps" in overview
        assert "active_ssps" in overview
        assert "total_requests" in overview
        assert "total_bids" in overview
        assert "overall_bid_rate" in overview
        print(f"PASS: SSP Analytics overview - {overview['total_ssps']} SSPs")
    
    def test_ssp_analytics_details(self):
        """Test GET /api/ssp-analytics/{ssp_id}/details"""
        endpoints = requests.get(f"{BASE_URL}/api/ssp-endpoints").json()
        if not endpoints:
            pytest.skip("No SSP endpoints available for testing")
        
        ssp_id = endpoints[0]["id"]
        response = requests.get(f"{BASE_URL}/api/ssp-analytics/{ssp_id}/details")
        assert response.status_code == 200
        
        data = response.json()
        assert "ssp" in data
        assert "metrics" in data
        assert "hourly_distribution" in data
        print(f"PASS: SSP Analytics details for {data['ssp']['name']}")


# ==================== BID OPTIMIZATION TESTS ====================

class TestBidOptimizationEndpoints:
    """Bid Optimization endpoint tests"""
    
    def test_bid_optimization_status(self):
        """Test GET /api/bid-optimization/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/bid-optimization/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_campaigns" in data
        assert "optimization_enabled_count" in data
        assert "campaigns" in data
        
        # Verify campaign structure
        if data["campaigns"]:
            campaign = data["campaigns"][0]
            assert "campaign_id" in campaign
            assert "campaign_name" in campaign
            assert "optimization_enabled" in campaign
            assert "target_win_rate" in campaign
        print(f"PASS: Bid optimization status - {data['optimization_enabled_count']} enabled")


# ==================== REFERENCE DATA TESTS ====================

class TestReferenceEndpoints:
    """Reference data endpoint tests"""
    
    def test_reference_all(self):
        """Test GET /api/reference/all endpoint"""
        response = requests.get(f"{BASE_URL}/api/reference/all")
        assert response.status_code == 200
        data = response.json()
        
        # Should contain IAB categories
        assert "iab_categories" in data
        assert isinstance(data["iab_categories"], dict)
        
        # Should have IAB1, IAB2, etc.
        assert "IAB1" in data["iab_categories"]
        print(f"PASS: Reference data - {len(data['iab_categories'])} IAB categories")
    
    def test_migration_matrix(self):
        """Test GET /api/migration-matrix endpoint"""
        response = requests.get(f"{BASE_URL}/api/migration-matrix")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        print(f"PASS: Migration matrix endpoint working")


# ==================== BID LOGS TESTS ====================

class TestBidLogsEndpoints:
    """Bid logs endpoint tests"""
    
    def test_get_bid_logs(self):
        """Test GET /api/bid-logs endpoint"""
        response = requests.get(f"{BASE_URL}/api/bid-logs")
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        
        assert isinstance(data["logs"], list)
        print(f"PASS: Bid logs - {data['total']} total logs")
    
    def test_get_bid_logs_pagination(self):
        """Test GET /api/bid-logs with pagination"""
        response = requests.get(f"{BASE_URL}/api/bid-logs?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["logs"]) <= 5
        assert data["limit"] == 5
        assert data["offset"] == 0
        print("PASS: Bid logs pagination working")


# ==================== PACING STATUS TESTS ====================

class TestPacingEndpoints:
    """Budget pacing endpoint tests"""
    
    def test_pacing_status(self):
        """Test GET /api/pacing/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/pacing/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "current_hour" in data
        assert "campaigns" in data
        assert isinstance(data["current_hour"], int)
        print(f"PASS: Pacing status - {len(data['campaigns'])} active campaigns")


# ==================== REPORTING TESTS ====================

class TestReportingEndpoints:
    """Reporting endpoint tests"""
    
    def test_report_summary(self):
        """Test GET /api/reports/summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/reports/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "start_date" in data
        assert "end_date" in data
        assert "summary" in data
        assert "daily_data" in data
        print("PASS: Report summary endpoint working")
    
    def test_campaign_report(self):
        """Test GET /api/reports/campaign/{id} endpoint"""
        campaigns = requests.get(f"{BASE_URL}/api/campaigns").json()
        if not campaigns:
            pytest.skip("No campaigns available for testing")
        
        campaign_id = campaigns[0]["id"]
        response = requests.get(f"{BASE_URL}/api/reports/campaign/{campaign_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "campaign_id" in data
        assert "summary" in data
        assert "daily_data" in data
        print(f"PASS: Campaign report for {data['campaign_name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
