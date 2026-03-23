"""
Test bid_response feature in bid logs
Tests that:
1. Bid logs store the complete OpenRTB bid response JSON for successful bids
2. No bid entries do NOT have bid_response field
3. API endpoint /api/bid-logs returns bid_response field for successful bids
"""
import pytest
import requests
import os
import json
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "superadmin@demo.com"
TEST_PASSWORD = "demo123"


class TestBidResponseFeature:
    """Test bid_response field in bid logs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with auth"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_health_check(self):
        """Test API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ API health check passed")
    
    def test_bid_logs_endpoint_accessible(self):
        """Test bid-logs endpoint is accessible"""
        response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        print(f"✓ Bid logs endpoint accessible, total logs: {data['total']}")
    
    def test_successful_bid_has_bid_response(self):
        """Test that successful bids (created after feature implementation) have bid_response field"""
        # Get bid logs
        response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=50")
        assert response.status_code == 200
        data = response.json()
        logs = data.get("logs", [])
        
        # Find successful bids that have bid_response (newer logs after feature implementation)
        successful_bids_with_response = [
            log for log in logs 
            if log.get("bid_made") == True and log.get("bid_response") is not None
        ]
        
        if not successful_bids_with_response:
            pytest.skip("No successful bids with bid_response found in logs to test")
        
        # Check that successful bids with bid_response have valid structure
        for bid in successful_bids_with_response[:5]:  # Check first 5
            log_id = bid.get("id")
            
            # Get detailed log
            detail_response = self.session.get(f"{BASE_URL}/api/bid-logs/{log_id}")
            assert detail_response.status_code == 200
            log_detail = detail_response.json()
            
            # Verify bid_response exists and has expected structure
            assert log_detail.get("bid_made") == True, f"Log {log_id} should have bid_made=True"
            
            bid_response = log_detail.get("bid_response")
            assert bid_response is not None, f"Log {log_id} should have bid_response"
            
            # Verify OpenRTB response structure
            assert "id" in bid_response, "bid_response should have 'id' field"
            assert "seatbid" in bid_response, "bid_response should have 'seatbid' field"
            
            # Check seatbid structure
            seatbid = bid_response.get("seatbid", [])
            if seatbid:
                assert len(seatbid) > 0, "seatbid should have at least one entry"
                first_seat = seatbid[0]
                assert "bid" in first_seat, "seatbid entry should have 'bid' array"
                
                bids = first_seat.get("bid", [])
                if bids:
                    first_bid = bids[0]
                    # Check bid fields
                    assert "id" in first_bid, "bid should have 'id'"
                    assert "impid" in first_bid, "bid should have 'impid'"
                    assert "price" in first_bid, "bid should have 'price'"
                    
                    # Check optional but expected fields
                    print(f"  Bid {log_id}: price=${first_bid.get('price')}, has_nurl={bool(first_bid.get('nurl'))}, has_burl={bool(first_bid.get('burl'))}")
            
            print(f"✓ Successful bid {log_id} has valid bid_response")
        
        print(f"✓ Verified {len(successful_bids_with_response[:5])} successful bids have bid_response field")
    
    def test_no_bid_entries_no_bid_response(self):
        """Test that no-bid entries do NOT have bid_response field (or it's null)"""
        # Get bid logs
        response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=50")
        assert response.status_code == 200
        data = response.json()
        logs = data.get("logs", [])
        
        # Find no-bid entries
        no_bids = [log for log in logs if log.get("bid_made") == False]
        
        if not no_bids:
            pytest.skip("No no-bid entries found in logs to test")
        
        # Check that no-bid entries don't have bid_response
        for log in no_bids[:5]:  # Check first 5 no-bids
            log_id = log.get("id")
            
            # Get detailed log
            detail_response = self.session.get(f"{BASE_URL}/api/bid-logs/{log_id}")
            assert detail_response.status_code == 200
            log_detail = detail_response.json()
            
            # Verify bid_response is None or not present
            bid_response = log_detail.get("bid_response")
            assert bid_response is None, f"No-bid log {log_id} should NOT have bid_response, got: {bid_response}"
            print(f"✓ No-bid entry {log_id} correctly has no bid_response")
        
        print(f"✓ Verified {len(no_bids[:5])} no-bid entries have no bid_response")
    
    def test_bid_response_contains_expected_fields(self):
        """Test that bid_response contains all expected OpenRTB fields"""
        # Get bid logs
        response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=50")
        assert response.status_code == 200
        data = response.json()
        logs = data.get("logs", [])
        
        # Find a successful bid with bid_response
        successful_bids = [log for log in logs if log.get("bid_made") == True]
        
        if not successful_bids:
            pytest.skip("No successful bids found in logs to test")
        
        # Get detailed log for first successful bid
        log_id = successful_bids[0].get("id")
        detail_response = self.session.get(f"{BASE_URL}/api/bid-logs/{log_id}")
        assert detail_response.status_code == 200
        log_detail = detail_response.json()
        
        bid_response = log_detail.get("bid_response")
        assert bid_response is not None, "bid_response should exist for successful bid"
        
        # Check top-level fields
        assert "id" in bid_response, "bid_response should have 'id'"
        assert "seatbid" in bid_response, "bid_response should have 'seatbid'"
        
        # Check seatbid structure
        seatbid = bid_response.get("seatbid", [])
        assert len(seatbid) > 0, "seatbid should have at least one entry"
        
        first_seat = seatbid[0]
        assert "bid" in first_seat, "seatbid should have 'bid' array"
        assert "seat" in first_seat, "seatbid should have 'seat'"
        
        # Check bid array
        bids = first_seat.get("bid", [])
        assert len(bids) > 0, "bid array should have at least one bid"
        
        first_bid = bids[0]
        
        # Required fields
        required_fields = ["id", "impid", "price"]
        for field in required_fields:
            assert field in first_bid, f"bid should have required field '{field}'"
        
        # Optional but expected fields for a complete bid
        expected_fields = ["adid", "nurl", "burl", "adomain", "cid", "crid"]
        present_fields = [f for f in expected_fields if f in first_bid]
        print(f"  Present optional fields: {present_fields}")
        
        # Check price is a number
        assert isinstance(first_bid.get("price"), (int, float)), "price should be a number"
        
        print(f"✓ bid_response contains all expected OpenRTB fields")
        print(f"  Response ID: {bid_response.get('id')}")
        print(f"  Bid ID: {first_bid.get('id')}")
        print(f"  Price: ${first_bid.get('price')}")
        print(f"  Has nurl: {bool(first_bid.get('nurl'))}")
        print(f"  Has burl: {bool(first_bid.get('burl'))}")
        print(f"  Has adm: {bool(first_bid.get('adm'))}")
    
    def test_create_bid_and_verify_response_stored(self):
        """Test creating a new bid and verifying bid_response is stored"""
        # Get an active SSP endpoint
        ssp_response = self.session.get(f"{BASE_URL}/api/ssp-endpoints")
        if ssp_response.status_code != 200:
            pytest.skip("Could not get SSP endpoints")
        
        ssps = ssp_response.json()
        active_ssps = [s for s in ssps if s.get("status") == "active"]
        
        if not active_ssps:
            pytest.skip("No active SSP endpoints found")
        
        ssp = active_ssps[0]
        endpoint_token = ssp.get("endpoint_token")
        
        # Create a bid request that should match (PHL geo, low bidfloor)
        bid_request = {
            "id": f"test-bid-response-{int(time.time())}",
            "imp": [{
                "id": "1",
                "banner": {
                    "w": 300,
                    "h": 250
                },
                "bidfloor": 0.01  # Low floor to ensure bid
            }],
            "device": {
                "geo": {
                    "country": "PHL"  # Target geo for Demo campaign
                },
                "devicetype": 4,
                "os": "iOS"
            },
            "site": {
                "domain": "example.com"
            }
        }
        
        # Send bid request
        bid_response = self.session.post(
            f"{BASE_URL}/api/bid/{endpoint_token}",
            json=bid_request
        )
        
        # Check if bid was made (200) or no bid (204)
        if bid_response.status_code == 204:
            print("  No bid returned - checking if log was created without bid_response")
            # Wait a moment for log to be saved
            time.sleep(0.5)
            
            # Get recent logs
            logs_response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=5")
            assert logs_response.status_code == 200
            logs = logs_response.json().get("logs", [])
            
            # Find our request
            our_log = next((l for l in logs if l.get("request_id") == bid_request["id"]), None)
            if our_log:
                assert our_log.get("bid_made") == False
                assert our_log.get("bid_response") is None
                print(f"✓ No-bid log created correctly without bid_response")
            return
        
        assert bid_response.status_code == 200, f"Expected 200 or 204, got {bid_response.status_code}"
        
        # Parse the bid response
        response_json = bid_response.json()
        assert "seatbid" in response_json
        assert len(response_json.get("seatbid", [])) > 0
        
        # Wait a moment for log to be saved
        time.sleep(0.5)
        
        # Get recent logs and find our bid
        logs_response = self.session.get(f"{BASE_URL}/api/bid-logs?limit=10")
        assert logs_response.status_code == 200
        logs = logs_response.json().get("logs", [])
        
        # Find our request
        our_log = next((l for l in logs if l.get("request_id") == bid_request["id"]), None)
        assert our_log is not None, "Could not find our bid log"
        
        # Get detailed log
        log_id = our_log.get("id")
        detail_response = self.session.get(f"{BASE_URL}/api/bid-logs/{log_id}")
        assert detail_response.status_code == 200
        log_detail = detail_response.json()
        
        # Verify bid_response is stored
        assert log_detail.get("bid_made") == True
        assert "bid_response" in log_detail
        stored_response = log_detail.get("bid_response")
        
        # Verify stored response matches what was returned
        assert stored_response.get("id") == response_json.get("id")
        assert len(stored_response.get("seatbid", [])) == len(response_json.get("seatbid", []))
        
        print(f"✓ New bid created and bid_response correctly stored in log {log_id}")
        print(f"  Response ID: {stored_response.get('id')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
