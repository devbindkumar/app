"""
Test 3-Tier RBAC Hierarchy and Admin Panel Features
Tests:
- Super Admin can ONLY create Admins (should fail for advertiser)
- Admin can ONLY create Advertisers (should fail for admin)
- New endpoints: stats, activity-timeline, users/search, users/export, dashboard-data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN_CREDS = {"email": "superadmin@demo.com", "password": "demo123"}
ADMIN_CREDS = {"email": "admin@demo.com", "password": "demo123"}
ADVERTISER_CREDS = {"email": "advertiser@demo.com", "password": "demo123"}


@pytest.fixture(scope="session")
def super_admin_token():
    """Get Super Admin token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN_CREDS)
    assert resp.status_code == 200, f"Super Admin login failed: {resp.text}"
    data = resp.json()
    return data.get("token") or data.get("access_token")


@pytest.fixture(scope="session")
def admin_token():
    """Get Admin token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    data = resp.json()
    return data.get("token") or data.get("access_token")


@pytest.fixture(scope="session")
def advertiser_token():
    """Get Advertiser token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=ADVERTISER_CREDS)
    assert resp.status_code == 200, f"Advertiser login failed: {resp.text}"
    data = resp.json()
    return data.get("token") or data.get("access_token")


class TestHierarchyEnforcement:
    """Test 3-tier hierarchy: Super Admin -> Admin -> Advertiser"""
    
    def test_super_admin_can_create_admin(self, super_admin_token):
        """Super Admin can ONLY create Admin accounts"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        user_data = {
            "name": "TEST_Admin_By_SA",
            "email": "test_admin_by_sa@test.com",
            "password": "testpass123",
            "role": "admin"
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should succeed
        assert resp.status_code in [200, 201], f"Super Admin should create Admin: {resp.text}"
        data = resp.json()
        assert data["role"] == "admin"
        assert data["email"] == "test_admin_by_sa@test.com"
        
        # Cleanup: Delete the test user
        user_id = data["id"]
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers)
    
    def test_super_admin_cannot_create_advertiser(self, super_admin_token):
        """Super Admin CANNOT create Advertiser accounts directly"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        user_data = {
            "name": "TEST_Advertiser_By_SA",
            "email": "test_adv_by_sa@test.com",
            "password": "testpass123",
            "role": "advertiser"
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should fail with 403
        assert resp.status_code == 403, f"Super Admin should NOT create Advertiser directly: {resp.text}"
        data = resp.json()
        assert "only create Admin" in data.get("detail", "")
    
    def test_admin_can_create_advertiser(self, admin_token):
        """Admin can ONLY create Advertiser accounts"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "name": "TEST_Advertiser_By_Admin",
            "email": "test_adv_by_admin@test.com",
            "password": "testpass123",
            "role": "advertiser"
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should succeed
        assert resp.status_code in [200, 201], f"Admin should create Advertiser: {resp.text}"
        data = resp.json()
        assert data["role"] == "advertiser"
        assert data["email"] == "test_adv_by_admin@test.com"
        
        # Store ID for cleanup
        user_id = data["id"]
        # Admin might not have delete permission, try with super admin
        sa_resp = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN_CREDS)
        sa_token = sa_resp.json().get("token") or sa_resp.json().get("access_token")
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers={"Authorization": f"Bearer {sa_token}"})
    
    def test_admin_cannot_create_admin(self, admin_token):
        """Admin CANNOT create Admin accounts"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "name": "TEST_Admin_By_Admin",
            "email": "test_admin_by_admin@test.com",
            "password": "testpass123",
            "role": "admin"
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should fail with 403
        assert resp.status_code == 403, f"Admin should NOT create Admin: {resp.text}"
        data = resp.json()
        assert "only create Advertiser" in data.get("detail", "")
    
    def test_advertiser_cannot_create_users(self, advertiser_token):
        """Advertiser CANNOT create any user accounts"""
        headers = {"Authorization": f"Bearer {advertiser_token}"}
        user_data = {
            "name": "TEST_User_By_Advertiser",
            "email": "test_by_advertiser@test.com",
            "password": "testpass123",
            "role": "advertiser"
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should fail with 403 (no permission)
        assert resp.status_code == 403, f"Advertiser should NOT create users: {resp.text}"


class TestStatsEndpoint:
    """Test GET /api/admin/stats endpoint"""
    
    def test_super_admin_gets_all_stats(self, super_admin_token):
        """Super Admin sees all stats including total_admins"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        resp = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert resp.status_code == 200, f"Stats endpoint failed: {resp.text}"
        data = resp.json()
        
        # Verify all expected fields
        assert "total_admins" in data
        assert "total_advertisers" in data
        assert "total_campaigns" in data
        assert "active_campaigns" in data
        assert "total_creatives" in data
        
        # Super Admin should have total_admins > 0 or >= 0
        assert isinstance(data["total_admins"], int)
        assert isinstance(data["total_advertisers"], int)
    
    def test_admin_gets_limited_stats(self, admin_token):
        """Admin sees only their own advertisers' stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert resp.status_code == 200, f"Stats endpoint failed for admin: {resp.text}"
        data = resp.json()
        
        # Admin should see total_admins = 0 (doesn't see other admins)
        assert data["total_admins"] == 0
        assert "total_advertisers" in data
        assert "total_campaigns" in data
    
    def test_advertiser_cannot_access_stats(self, advertiser_token):
        """Advertiser should not have access to admin stats"""
        headers = {"Authorization": f"Bearer {advertiser_token}"}
        resp = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        # Should fail - advertiser doesn't have admin access
        assert resp.status_code == 403, f"Advertiser should not access admin stats"


class TestActivityTimeline:
    """Test GET /api/admin/activity-timeline endpoint"""
    
    def test_super_admin_gets_activity_timeline(self, super_admin_token):
        """Super Admin can access activity timeline"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        resp = requests.get(f"{BASE_URL}/api/admin/activity-timeline?limit=10", headers=headers)
        
        assert resp.status_code == 200, f"Activity timeline failed: {resp.text}"
        data = resp.json()
        
        assert "activities" in data
        assert "total" in data
        assert isinstance(data["activities"], list)
        
        # If there are activities, check structure
        if len(data["activities"]) > 0:
            activity = data["activities"][0]
            assert "timestamp" in activity
            assert "action" in activity
            assert "actor_name" in activity
    
    def test_admin_gets_activity_timeline(self, admin_token):
        """Admin can access activity timeline (limited to their data)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = requests.get(f"{BASE_URL}/api/admin/activity-timeline?limit=5", headers=headers)
        
        assert resp.status_code == 200, f"Activity timeline failed for admin: {resp.text}"
        data = resp.json()
        assert "activities" in data


class TestUserSearch:
    """Test GET /api/admin/users/search endpoint"""
    
    def test_super_admin_search_users(self, super_admin_token):
        """Super Admin can search all users"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Search with empty query (get all)
        resp = requests.get(f"{BASE_URL}/api/admin/users/search?q=", headers=headers)
        assert resp.status_code == 200, f"Search failed: {resp.text}"
        users = resp.json()
        assert isinstance(users, list)
    
    def test_search_with_query(self, super_admin_token):
        """Search by name/email"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/users/search?q=admin", headers=headers)
        assert resp.status_code == 200
        users = resp.json()
        
        # Should find admin-related users
        assert isinstance(users, list)
    
    def test_search_with_role_filter(self, super_admin_token):
        """Search with role filter"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/users/search?q=&role=admin", headers=headers)
        assert resp.status_code == 200
        users = resp.json()
        
        # All returned users should be admins
        for user in users:
            assert user["role"] == "admin"


class TestExportCSV:
    """Test GET /api/admin/users/export endpoint"""
    
    def test_super_admin_export_csv(self, super_admin_token):
        """Super Admin can export users to CSV"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/users/export", headers=headers)
        
        assert resp.status_code == 200, f"Export failed: {resp.text}"
        assert "text/csv" in resp.headers.get("content-type", "")
        
        # Check CSV content
        content = resp.text
        assert "Name,Email,Role,Status,Created At,Created By" in content
    
    def test_admin_export_csv(self, admin_token):
        """Admin can export their advertisers to CSV"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/users/export", headers=headers)
        
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")


class TestAdvertiserDashboardData:
    """Test GET /api/admin/advertiser/{id}/dashboard-data endpoint"""
    
    def test_get_advertiser_dashboard_data(self, super_admin_token):
        """Super Admin can view advertiser dashboard data"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # First get list of advertisers
        resp = requests.get(f"{BASE_URL}/api/admin/users/search?q=&role=advertiser", headers=headers)
        advertisers = resp.json()
        
        if len(advertisers) > 0:
            adv_id = advertisers[0]["id"]
            resp = requests.get(f"{BASE_URL}/api/admin/advertiser/{adv_id}/dashboard-data", headers=headers)
            
            assert resp.status_code == 200, f"Advertiser dashboard failed: {resp.text}"
            data = resp.json()
            
            # Verify structure
            assert "advertiser" in data
            assert "stats" in data
            assert "campaigns" in data
            
            assert data["advertiser"]["id"] == adv_id
            assert "total_campaigns" in data["stats"]
            assert "active_campaigns" in data["stats"]
            assert "total_creatives" in data["stats"]
    
    def test_invalid_advertiser_id(self, super_admin_token):
        """Test with invalid advertiser ID"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/advertiser/invalid-id-123/dashboard-data", headers=headers)
        assert resp.status_code == 404


class TestAdminDashboardData:
    """Test GET /api/admin/admin/{id}/dashboard-data endpoint (Super Admin only)"""
    
    def test_super_admin_view_admin_dashboard(self, super_admin_token):
        """Super Admin can view another admin's dashboard data"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # First get list of admins
        resp = requests.get(f"{BASE_URL}/api/admin/users/search?q=&role=admin", headers=headers)
        admins = resp.json()
        
        if len(admins) > 0:
            admin_id = admins[0]["id"]
            resp = requests.get(f"{BASE_URL}/api/admin/admin/{admin_id}/dashboard-data", headers=headers)
            
            assert resp.status_code == 200, f"Admin dashboard failed: {resp.text}"
            data = resp.json()
            
            # Verify structure
            assert "admin" in data
            assert "stats" in data
            assert "advertisers" in data
            
            assert data["admin"]["id"] == admin_id
            assert "total_advertisers" in data["stats"]
            assert "total_campaigns" in data["stats"]
    
    def test_admin_cannot_view_other_admin_dashboard(self, admin_token):
        """Admin cannot use admin dashboard endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/admin/admin/some-admin-id/dashboard-data", headers=headers)
        assert resp.status_code == 403, "Admin should not access other admin's dashboard"


class TestUserRoleNoUserRole:
    """Verify the 'User' role has been removed from the system"""
    
    def test_cannot_create_user_role(self, super_admin_token):
        """System should not allow creating users with 'user' role"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        user_data = {
            "name": "TEST_User_Role",
            "email": "test_user_role@test.com",
            "password": "testpass123",
            "role": "user"  # This role should not exist
        }
        resp = requests.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
        
        # Should fail - user role doesn't exist
        assert resp.status_code in [400, 403, 422], f"Should not create 'user' role: {resp.text}"
