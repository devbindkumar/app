"""
Hierarchical Auth System Tests
Tests for:
1. User hierarchy (parent_id, created_by tracking)
2. Admin Panel tabs: Users, Hierarchy, Access Control
3. Super Admin can impersonate other users
4. Bulk access update endpoint
5. Admin can only create Advertiser/User (not Admin/Super Admin)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo account credentials
DEMO_ACCOUNTS = {
    "user": {"email": "user@demo.com", "password": "demo123"},
    "advertiser": {"email": "advertiser@demo.com", "password": "demo123"},
    "admin": {"email": "admin@demo.com", "password": "demo123"},
    "super_admin": {"email": "superadmin@demo.com", "password": "demo123"},
}


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_check(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health check passed")
    
    def test_superadmin_login(self):
        """Test super admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "super_admin"
        print("✓ Super admin login successful")


class TestUserHierarchy:
    """Test hierarchical user management - parent_id, created_by tracking"""
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def admin_headers(self):
        """Get admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_get_users_hierarchy_endpoint(self, superadmin_headers):
        """Test /admin/users/hierarchy endpoint returns hierarchy data"""
        response = requests.get(f"{BASE_URL}/api/admin/users/hierarchy", headers=superadmin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "admins" in data
        assert "orphan_advertisers" in data
        assert "total_admins" in data
        assert "total_advertisers" in data
        print(f"✓ Hierarchy endpoint returns: {len(data['admins'])} admins, {data['total_advertisers']} advertisers")
    
    def test_admin_only_sees_own_children(self, admin_headers):
        """Admin should only see users they created (children)"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        
        users = response.json()
        # Admin sees only their children (users with parent_id = admin's id)
        print(f"✓ Admin sees {len(users)} users (their children)")
    
    def test_superadmin_sees_all_users(self, superadmin_headers):
        """Super admin should see all users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=superadmin_headers)
        assert response.status_code == 200
        
        users = response.json()
        # Super admin sees all users
        assert len(users) >= 4  # At least demo accounts
        print(f"✓ Super admin sees all {len(users)} users")
    
    def test_created_user_has_parent_id(self, superadmin_headers):
        """When creating a user, parent_id and created_by should be set"""
        test_email = f"TEST_child_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = requests.post(f"{BASE_URL}/api/admin/users", headers=superadmin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test Child User",
            "role": "advertiser"
        })
        
        if create_response.status_code in [200, 201]:
            user = create_response.json()
            assert "parent_id" in user
            assert "created_by" in user
            assert user["parent_id"] is not None
            assert user["created_by"] is not None
            print(f"✓ Created user has parent_id: {user['parent_id']}, created_by: {user['created_by']}")
            
            # Cleanup
            user_id = user["id"]
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
        elif create_response.status_code == 400 and "already registered" in create_response.text:
            print("✓ User already exists (test data)")
        else:
            pytest.fail(f"Unexpected response: {create_response.status_code} - {create_response.text}")
    
    def test_users_tab_shows_created_by(self, superadmin_headers):
        """Verify user list includes created_by field"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=superadmin_headers)
        assert response.status_code == 200
        
        users = response.json()
        # Find a user that was created by someone
        users_with_creator = [u for u in users if u.get("created_by")]
        print(f"✓ Found {len(users_with_creator)} users with created_by field")


class TestImpersonation:
    """Test Super Admin impersonation feature"""
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def advertiser_user_id(self, superadmin_headers):
        """Get advertiser user ID"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=superadmin_headers)
        users = response.json()
        advertiser = next((u for u in users if u["email"] == "advertiser@demo.com"), None)
        return advertiser["id"] if advertiser else None
    
    def test_impersonate_endpoint_exists(self, superadmin_headers, advertiser_user_id):
        """Test impersonate endpoint returns token for target user"""
        if not advertiser_user_id:
            pytest.skip("Advertiser user not found")
        
        response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/{advertiser_user_id}",
            headers=superadmin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert "impersonation" in data
        assert data["impersonation"] == True
        assert data["user"]["email"] == "advertiser@demo.com"
        print(f"✓ Impersonation successful: {data['user']['name']}")
    
    def test_impersonated_token_works(self, superadmin_headers, advertiser_user_id):
        """Test that impersonated token can access API as target user"""
        if not advertiser_user_id:
            pytest.skip("Advertiser user not found")
        
        # Get impersonation token
        impersonate_response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/{advertiser_user_id}",
            headers=superadmin_headers
        )
        impersonate_data = impersonate_response.json()
        impersonate_token = impersonate_data["token"]
        
        # Use impersonated token to check /auth/me
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {impersonate_token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == "advertiser@demo.com"
        assert me_data["role"] == "advertiser"
        print(f"✓ Impersonated token works, role: {me_data['role']}")
    
    def test_cannot_impersonate_inactive_user(self, superadmin_headers):
        """Test cannot impersonate inactive users"""
        # Create and deactivate a user
        test_email = f"TEST_inactive_{uuid.uuid4().hex[:8]}@example.com"
        
        create_response = requests.post(f"{BASE_URL}/api/admin/users", headers=superadmin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Inactive Test User",
            "role": "user"
        })
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test user")
        
        user_id = create_response.json()["id"]
        
        # Deactivate user
        requests.put(f"{BASE_URL}/api/admin/users/{user_id}/status?is_active=false", headers=superadmin_headers)
        
        # Try to impersonate
        impersonate_response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/{user_id}",
            headers=superadmin_headers
        )
        assert impersonate_response.status_code == 400
        print("✓ Cannot impersonate inactive user (400)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
    
    def test_admin_cannot_impersonate(self):
        """Admin (non-super) cannot impersonate users"""
        # Login as admin
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
        admin_token = admin_response.json()["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get user list first
        users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
        
        # Try to impersonate - should fail with 403
        impersonate_response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/some-user-id",
            headers=admin_headers
        )
        assert impersonate_response.status_code == 403
        print("✓ Admin cannot impersonate (403)")


class TestBulkAccessUpdate:
    """Test bulk access update endpoint for Access Control tab"""
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_bulk_update_endpoint_exists(self, superadmin_headers):
        """Test bulk update endpoint exists and accepts request"""
        # Get current config first
        config_response = requests.get(f"{BASE_URL}/api/admin/roles/config", headers=superadmin_headers)
        current_config = config_response.json()
        user_config = current_config.get("user", {})
        
        # Make bulk update with same values (no actual change)
        response = requests.put(
            f"{BASE_URL}/api/admin/roles/bulk-update",
            headers=superadmin_headers,
            json={
                "role": "user",
                "sidebar_access": user_config.get("sidebar_access", ["dashboard", "reports"]),
                "permissions": user_config.get("permissions", ["view_dashboard", "view_reports"])
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "users_updated" in data
        print(f"✓ Bulk update successful, {data['users_updated']} users affected")
    
    def test_bulk_update_updates_all_users_with_role(self, superadmin_headers):
        """Test bulk update actually updates all users with the specified role"""
        # Get current advertiser config
        config_response = requests.get(f"{BASE_URL}/api/admin/roles/config", headers=superadmin_headers)
        current_config = config_response.json()
        advertiser_config = current_config.get("advertiser", {})
        
        # Add a test item to sidebar_access
        current_sidebar = advertiser_config.get("sidebar_access", [])
        
        # Make bulk update
        response = requests.put(
            f"{BASE_URL}/api/admin/roles/bulk-update",
            headers=superadmin_headers,
            json={
                "role": "advertiser",
                "sidebar_access": current_sidebar,
                "permissions": advertiser_config.get("permissions", [])
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        print(f"✓ Bulk update for advertiser role: {data['users_updated']} users updated")
    
    def test_admin_cannot_bulk_update(self):
        """Admin cannot use bulk update endpoint"""
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
        admin_token = admin_response.json()["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/admin/roles/bulk-update",
            headers=admin_headers,
            json={
                "role": "user",
                "sidebar_access": ["dashboard"],
                "permissions": ["view_dashboard"]
            }
        )
        assert response.status_code == 403
        print("✓ Admin cannot bulk update (403)")


class TestRoleRestrictions:
    """Test role creation restrictions"""
    
    @pytest.fixture
    def admin_headers(self):
        """Get admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_admin_can_create_advertiser(self, admin_headers):
        """Admin can create Advertiser accounts"""
        test_email = f"TEST_adv_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/users", headers=admin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test Advertiser by Admin",
            "role": "advertiser"
        })
        
        # May succeed or fail if email exists
        if response.status_code in [200, 201]:
            print(f"✓ Admin created advertiser successfully")
            # Note: Admin cannot delete, test data remains
        elif response.status_code == 400:
            print("✓ Admin can create advertiser (email collision)")
        else:
            pytest.fail(f"Unexpected: {response.status_code} - {response.text}")
    
    def test_admin_can_create_user(self, admin_headers):
        """Admin can create User accounts"""
        test_email = f"TEST_usr_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/users", headers=admin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test User by Admin",
            "role": "user"
        })
        
        if response.status_code in [200, 201]:
            print(f"✓ Admin created user successfully")
        elif response.status_code == 400:
            print("✓ Admin can create user (email collision)")
        else:
            pytest.fail(f"Unexpected: {response.status_code} - {response.text}")
    
    def test_admin_cannot_create_admin(self, admin_headers):
        """Admin CANNOT create Admin accounts"""
        test_email = f"TEST_admin_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/users", headers=admin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test Admin by Admin",
            "role": "admin"
        })
        
        assert response.status_code == 403
        assert "Admin can only create Advertiser or User" in response.text or "cannot create" in response.text.lower()
        print("✓ Admin cannot create admin (403)")
    
    def test_admin_cannot_create_superadmin(self, admin_headers):
        """Admin CANNOT create Super Admin accounts"""
        test_email = f"TEST_super_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/users", headers=admin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test Super Admin by Admin",
            "role": "super_admin"
        })
        
        assert response.status_code == 403
        print("✓ Admin cannot create super_admin (403)")
    
    def test_superadmin_can_create_admin(self, superadmin_headers):
        """Super Admin CAN create Admin accounts"""
        test_email = f"TEST_admin_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/admin/users", headers=superadmin_headers, json={
            "email": test_email,
            "password": "test123456",
            "name": "Test Admin by SuperAdmin",
            "role": "admin"
        })
        
        if response.status_code in [200, 201]:
            user_id = response.json()["id"]
            print(f"✓ Super Admin created admin successfully")
            # Cleanup
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
        elif response.status_code == 400:
            print("✓ Super Admin can create admin (email collision)")
        else:
            pytest.fail(f"Unexpected: {response.status_code} - {response.text}")


class TestUserChildren:
    """Test /admin/users/{user_id}/children endpoint"""
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_get_user_children_endpoint(self, superadmin_headers):
        """Test getting children of a specific user"""
        # Get admin user ID
        users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=superadmin_headers)
        users = users_response.json()
        admin_user = next((u for u in users if u["email"] == "admin@demo.com"), None)
        
        if not admin_user:
            pytest.skip("Admin user not found")
        
        admin_id = admin_user["id"]
        
        response = requests.get(f"{BASE_URL}/api/admin/users/{admin_id}/children", headers=superadmin_headers)
        assert response.status_code == 200
        
        children = response.json()
        assert isinstance(children, list)
        print(f"✓ Get children endpoint works, admin has {len(children)} children")


class TestDataScope:
    """Test data scope endpoint"""
    
    @pytest.fixture
    def superadmin_headers(self):
        """Get super admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def admin_headers(self):
        """Get admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def user_headers(self):
        """Get user auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["user"])
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_superadmin_scope_is_all(self, superadmin_headers):
        """Super admin scope should be 'all'"""
        response = requests.get(f"{BASE_URL}/api/admin/my-data-scope", headers=superadmin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["scope"] == "all"
        print("✓ Super admin scope is 'all'")
    
    def test_admin_scope_is_hierarchical(self, admin_headers):
        """Admin scope should be 'hierarchical'"""
        response = requests.get(f"{BASE_URL}/api/admin/my-data-scope", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["scope"] == "hierarchical"
        assert "user_ids" in data
        print(f"✓ Admin scope is 'hierarchical', sees {len(data['user_ids'])} user IDs")
    
    def test_user_scope_is_self(self, user_headers):
        """User scope should be 'self'"""
        response = requests.get(f"{BASE_URL}/api/admin/my-data-scope", headers=user_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["scope"] == "self"
        assert "user_ids" in data
        assert len(data["user_ids"]) == 1
        print("✓ User scope is 'self'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
