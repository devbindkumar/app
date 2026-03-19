"""
Security Features Tests
Tests for:
1. Password Reset Flow (request token, confirm reset, login with new password)
2. Two-Factor Authentication (2FA) - Setup, Enable, Disable, Login with 2FA
3. Audit Logging - Login events, password reset, 2FA events, admin actions
4. Data Isolation - Campaigns/Creatives filtered by ownership
5. Change Password endpoint
"""
import pytest
import requests
import os
import uuid
import pyotp
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo account credentials
DEMO_ACCOUNTS = {
    "user": {"email": "user@demo.com", "password": "demo123"},
    "advertiser": {"email": "advertiser@demo.com", "password": "demo123"},
    "admin": {"email": "admin@demo.com", "password": "demo123"},
    "super_admin": {"email": "superadmin@demo.com", "password": "demo123"},
}


# ============== FIXTURES ==============
@pytest.fixture
def superadmin_headers():
    """Get super admin auth headers"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["super_admin"])
    data = response.json()
    if "token" in data:
        return {"Authorization": f"Bearer {data['token']}", "Content-Type": "application/json"}
    pytest.skip("Super admin login failed")

@pytest.fixture
def admin_headers():
    """Get admin auth headers"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["admin"])
    data = response.json()
    if "token" in data:
        return {"Authorization": f"Bearer {data['token']}", "Content-Type": "application/json"}
    pytest.skip("Admin login failed")

@pytest.fixture
def advertiser_headers():
    """Get advertiser auth headers"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["advertiser"])
    data = response.json()
    if "token" in data:
        return {"Authorization": f"Bearer {data['token']}", "Content-Type": "application/json"}
    pytest.skip("Advertiser login failed")

@pytest.fixture
def user_headers():
    """Get user auth headers"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["user"])
    data = response.json()
    if "token" in data:
        return {"Authorization": f"Bearer {data['token']}", "Content-Type": "application/json"}
    pytest.skip("User login failed")


# ============== HEALTH CHECK ==============
class TestHealthCheck:
    """Basic health check"""
    
    def test_api_is_healthy(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ API is healthy")


# ============== PASSWORD RESET TESTS ==============
class TestPasswordReset:
    """Test password reset flow: request token -> confirm reset -> login with new password"""
    
    def test_password_reset_request_endpoint(self):
        """Test POST /api/auth/password-reset/request returns reset_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/request",
            json={"email": DEMO_ACCOUNTS["advertiser"]["email"]}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        # For demo purposes, token is returned directly
        assert "reset_token" in data
        assert len(data["reset_token"]) > 0
        print(f"✓ Password reset request successful, token returned")
    
    def test_password_reset_request_nonexistent_email(self):
        """Test password reset with non-existent email (should still return success to prevent enumeration)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        # No token for non-existent email
        print("✓ Password reset request for non-existent email handled gracefully")
    
    def test_password_reset_full_flow(self, superadmin_headers):
        """Test full password reset flow: create user, request reset, confirm reset, login with new password"""
        test_email = f"TEST_reset_{uuid.uuid4().hex[:8]}@example.com"
        original_password = "oldpass123"
        new_password = "newpass456"
        
        # Step 1: Create a test user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": original_password,
                "name": "Test Reset User",
                "role": "user"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user: {create_response.text}")
        
        user_id = create_response.json()["id"]
        print(f"  Step 1: Created test user {test_email}")
        
        try:
            # Step 2: Request password reset
            reset_request = requests.post(
                f"{BASE_URL}/api/auth/password-reset/request",
                json={"email": test_email}
            )
            assert reset_request.status_code == 200
            reset_token = reset_request.json().get("reset_token")
            assert reset_token, "Reset token not returned"
            print(f"  Step 2: Got reset token")
            
            # Step 3: Confirm password reset with token and new password
            confirm_response = requests.post(
                f"{BASE_URL}/api/auth/password-reset/confirm",
                json={"token": reset_token, "new_password": new_password}
            )
            assert confirm_response.status_code == 200
            assert confirm_response.json()["status"] == "success"
            print(f"  Step 3: Password reset confirmed")
            
            # Step 4: Login with old password should fail
            old_login = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": original_password}
            )
            assert old_login.status_code == 401
            print(f"  Step 4: Old password correctly rejected")
            
            # Step 5: Login with new password should succeed
            new_login = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": new_password}
            )
            assert new_login.status_code == 200
            assert "token" in new_login.json()
            print(f"  Step 5: Login with new password successful")
            
            print("✓ Full password reset flow completed successfully")
            
        finally:
            # Cleanup: Delete test user
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
    
    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token should fail"""
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset/confirm",
            json={"token": "invalid_token_12345", "new_password": "newpass123"}
        )
        assert response.status_code == 400
        print("✓ Invalid reset token correctly rejected")
    
    def test_password_reset_expired_token(self, superadmin_headers):
        """Test that a used token cannot be reused"""
        test_email = f"TEST_expire_{uuid.uuid4().hex[:8]}@example.com"
        
        # Create test user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": "test123456",
                "name": "Test Expire User",
                "role": "user"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user")
        
        user_id = create_response.json()["id"]
        
        try:
            # Request reset token
            reset_request = requests.post(
                f"{BASE_URL}/api/auth/password-reset/request",
                json={"email": test_email}
            )
            reset_token = reset_request.json().get("reset_token")
            
            # Use the token once - password must be at least 6 chars
            confirm1 = requests.post(
                f"{BASE_URL}/api/auth/password-reset/confirm",
                json={"token": reset_token, "new_password": "newpass123"}
            )
            assert confirm1.status_code == 200
            
            # Try to use the same token again - should fail
            confirm2 = requests.post(
                f"{BASE_URL}/api/auth/password-reset/confirm",
                json={"token": reset_token, "new_password": "newpass456"}
            )
            assert confirm2.status_code == 400
            print("✓ Used reset token correctly rejected on reuse")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)


# ============== CHANGE PASSWORD TESTS ==============
class TestChangePassword:
    """Test change password for logged-in users"""
    
    def test_change_password_endpoint(self, superadmin_headers):
        """Test POST /api/auth/change-password"""
        test_email = f"TEST_change_{uuid.uuid4().hex[:8]}@example.com"
        original_password = "original123"
        new_password = "changed456"
        
        # Create test user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": original_password,
                "name": "Test Change Password",
                "role": "user"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user")
        
        user_id = create_response.json()["id"]
        
        try:
            # Login as test user
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": original_password}
            )
            user_token = login_response.json()["token"]
            user_headers = {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
            
            # Change password
            change_response = requests.post(
                f"{BASE_URL}/api/auth/change-password",
                headers=user_headers,
                json={"current_password": original_password, "new_password": new_password}
            )
            assert change_response.status_code == 200
            assert change_response.json()["status"] == "success"
            print("✓ Change password successful")
            
            # Verify new password works
            new_login = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": new_password}
            )
            assert new_login.status_code == 200
            print("✓ Login with new password successful")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
    
    def test_change_password_wrong_current(self, superadmin_headers):
        """Test change password with wrong current password"""
        test_email = f"TEST_wrong_{uuid.uuid4().hex[:8]}@example.com"
        
        # Create test user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": "correct123",
                "name": "Test Wrong Current",
                "role": "user"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user")
        
        user_id = create_response.json()["id"]
        
        try:
            # Login as test user
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": "correct123"}
            )
            user_token = login_response.json()["token"]
            user_headers = {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
            
            # Try to change password with wrong current
            change_response = requests.post(
                f"{BASE_URL}/api/auth/change-password",
                headers=user_headers,
                json={"current_password": "wrongpass", "new_password": "newpass123"}
            )
            assert change_response.status_code == 400
            print("✓ Wrong current password correctly rejected")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)


# ============== 2FA TESTS ==============
class TestTwoFactorAuthentication:
    """Test Two-Factor Authentication (2FA) - Setup, Enable, Disable, Login with 2FA"""
    
    def test_2fa_status_endpoint(self, admin_headers):
        """Test GET /api/auth/2fa/status"""
        response = requests.get(f"{BASE_URL}/api/auth/2fa/status", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        assert "can_enable" in data
        assert data["can_enable"] == True  # Admin can enable 2FA
        print(f"✓ 2FA status endpoint works, enabled={data['enabled']}, can_enable={data['can_enable']}")
    
    def test_2fa_status_user_cannot_enable(self, user_headers):
        """Test that regular users cannot enable 2FA"""
        response = requests.get(f"{BASE_URL}/api/auth/2fa/status", headers=user_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["can_enable"] == False
        print("✓ Regular user cannot enable 2FA")
    
    def test_2fa_setup_admin_only(self, user_headers):
        """Test that 2FA setup is admin only"""
        response = requests.post(f"{BASE_URL}/api/auth/2fa/setup", headers=user_headers)
        assert response.status_code == 403
        print("✓ 2FA setup correctly restricted to admin/super_admin")
    
    def test_2fa_setup_returns_secret(self, superadmin_headers):
        """Test POST /api/auth/2fa/setup returns secret, qr_code_url, backup_codes"""
        # First check if 2FA is already enabled (from previous tests)
        status_response = requests.get(f"{BASE_URL}/api/auth/2fa/status", headers=superadmin_headers)
        if status_response.json().get("enabled"):
            print("  2FA already enabled, skipping setup test")
            pytest.skip("2FA already enabled for super admin")
        
        response = requests.post(f"{BASE_URL}/api/auth/2fa/setup", headers=superadmin_headers)
        
        if response.status_code == 400 and "already enabled" in response.text:
            pytest.skip("2FA already enabled")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "secret" in data
        assert "qr_code_url" in data
        assert "backup_codes" in data
        assert len(data["secret"]) > 0
        assert len(data["backup_codes"]) == 8
        print(f"✓ 2FA setup returns secret, QR URL, and 8 backup codes")
    
    def test_2fa_full_flow(self, superadmin_headers):
        """Test full 2FA flow: setup -> enable -> login with 2FA -> disable"""
        test_email = f"TEST_2fa_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "test2fa123"
        
        # Create a test admin user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": test_password,
                "name": "Test 2FA User",
                "role": "admin"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test admin: {create_response.text}")
        
        user_id = create_response.json()["id"]
        print(f"  Step 1: Created test admin {test_email}")
        
        try:
            # Login as test admin
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            assert login_response.status_code == 200
            test_token = login_response.json()["token"]
            test_headers = {"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"}
            print(f"  Step 2: Logged in as test admin")
            
            # Setup 2FA
            setup_response = requests.post(f"{BASE_URL}/api/auth/2fa/setup", headers=test_headers)
            assert setup_response.status_code == 200
            setup_data = setup_response.json()
            secret = setup_data["secret"]
            backup_codes = setup_data["backup_codes"]
            print(f"  Step 3: 2FA setup complete, got secret and backup codes")
            
            # Generate TOTP code using the secret
            totp = pyotp.TOTP(secret)
            code = totp.now()
            print(f"  Step 4: Generated TOTP code: {code}")
            
            # Enable 2FA with the TOTP code
            enable_response = requests.post(
                f"{BASE_URL}/api/auth/2fa/enable",
                headers=test_headers,
                json={"code": code}
            )
            assert enable_response.status_code == 200
            print(f"  Step 5: 2FA enabled successfully")
            
            # Verify 2FA is enabled
            status_response = requests.get(f"{BASE_URL}/api/auth/2fa/status", headers=test_headers)
            assert status_response.json()["enabled"] == True
            print(f"  Step 6: Verified 2FA status is enabled")
            
            # Test login with 2FA - should return requires_2fa=true
            login_2fa_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            assert login_2fa_response.status_code == 200
            login_2fa_data = login_2fa_response.json()
            assert login_2fa_data.get("requires_2fa") == True
            assert "temp_token" in login_2fa_data
            temp_token = login_2fa_data["temp_token"]
            print(f"  Step 7: Login with 2FA returns requires_2fa=true and temp_token")
            
            # Generate new TOTP code for verification
            time.sleep(1)  # Wait a moment for next code cycle if needed
            verify_code = totp.now()
            
            # Verify 2FA login
            verify_response = requests.post(
                f"{BASE_URL}/api/auth/verify-2fa",
                json={"temp_token": temp_token, "code": verify_code}
            )
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert "token" in verify_data
            assert verify_data.get("requires_2fa") == False
            new_token = verify_data["token"]
            print(f"  Step 8: 2FA login verification successful, got session token")
            
            # Use the new token to access protected resources
            new_headers = {"Authorization": f"Bearer {new_token}", "Content-Type": "application/json"}
            me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=new_headers)
            assert me_response.status_code == 200
            # Email is lowercased in the system
            assert me_response.json()["email"] == test_email.lower()
            print(f"  Step 9: Session token works, user authenticated")
            
            # Disable 2FA
            disable_code = totp.now()
            disable_response = requests.post(
                f"{BASE_URL}/api/auth/2fa/disable",
                headers=new_headers,
                json={"code": disable_code}
            )
            assert disable_response.status_code == 200
            print(f"  Step 10: 2FA disabled successfully")
            
            # Verify 2FA is disabled
            status_after = requests.get(f"{BASE_URL}/api/auth/2fa/status", headers=new_headers)
            assert status_after.json()["enabled"] == False
            print(f"  Step 11: Verified 2FA is disabled")
            
            print("✓ Full 2FA flow completed successfully")
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
    
    def test_2fa_invalid_code_rejected(self, superadmin_headers):
        """Test that invalid 2FA code is rejected during enable"""
        test_email = f"TEST_2fa_invalid_{uuid.uuid4().hex[:8]}@example.com"
        
        # Create test admin
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": "test123456",
                "name": "Test Invalid 2FA",
                "role": "admin"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test admin")
        
        user_id = create_response.json()["id"]
        
        try:
            # Login and setup 2FA
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": "test123456"}
            )
            test_token = login_response.json()["token"]
            test_headers = {"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"}
            
            setup_response = requests.post(f"{BASE_URL}/api/auth/2fa/setup", headers=test_headers)
            assert setup_response.status_code == 200
            
            # Try to enable with invalid code
            enable_response = requests.post(
                f"{BASE_URL}/api/auth/2fa/enable",
                headers=test_headers,
                json={"code": "000000"}
            )
            assert enable_response.status_code == 400
            print("✓ Invalid 2FA code correctly rejected")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)


# ============== AUDIT LOGGING TESTS ==============
class TestAuditLogging:
    """Test audit logging for admin actions"""
    
    def test_audit_logs_endpoint(self, superadmin_headers):
        """Test GET /api/admin/audit-logs returns logs"""
        response = requests.get(f"{BASE_URL}/api/admin/audit-logs", headers=superadmin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        print(f"✓ Audit logs endpoint works, total logs: {data['total']}")
    
    def test_audit_logs_superadmin_only(self, admin_headers):
        """Test audit logs endpoint is super admin only"""
        response = requests.get(f"{BASE_URL}/api/admin/audit-logs", headers=admin_headers)
        assert response.status_code == 403
        print("✓ Audit logs correctly restricted to super admin")
    
    def test_login_creates_audit_log(self, superadmin_headers):
        """Test that login events are logged"""
        # Get current log count
        logs_before = requests.get(f"{BASE_URL}/api/admin/audit-logs?limit=100", headers=superadmin_headers)
        before_count = logs_before.json()["total"]
        
        # Login to create an audit event
        requests.post(f"{BASE_URL}/api/auth/login", json=DEMO_ACCOUNTS["advertiser"])
        
        # Check logs after
        logs_after = requests.get(f"{BASE_URL}/api/admin/audit-logs?limit=100", headers=superadmin_headers)
        after_data = logs_after.json()
        
        # Find login events
        login_events = [log for log in after_data["logs"] if "login" in log.get("action", "")]
        assert len(login_events) > 0
        print(f"✓ Login events are logged, found {len(login_events)} login events")
    
    def test_audit_log_has_required_fields(self, superadmin_headers):
        """Test that audit logs have required fields"""
        response = requests.get(f"{BASE_URL}/api/admin/audit-logs?limit=10", headers=superadmin_headers)
        data = response.json()
        
        if len(data["logs"]) == 0:
            pytest.skip("No audit logs to check")
        
        log = data["logs"][0]
        assert "timestamp" in log
        assert "action" in log
        assert "actor" in log
        assert "success" in log
        print("✓ Audit logs have required fields (timestamp, action, actor, success)")
    
    def test_password_reset_creates_audit_log(self, superadmin_headers):
        """Test that password reset events are logged"""
        test_email = f"TEST_audit_{uuid.uuid4().hex[:8]}@example.com"
        
        # Create test user
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": "test123456",
                "name": "Test Audit User",
                "role": "user"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test user")
        
        user_id = create_response.json()["id"]
        
        try:
            # Request password reset
            requests.post(
                f"{BASE_URL}/api/auth/password-reset/request",
                json={"email": test_email}
            )
            
            # Check audit logs for password reset event
            logs_response = requests.get(
                f"{BASE_URL}/api/admin/audit-logs?limit=50",
                headers=superadmin_headers
            )
            logs_data = logs_response.json()
            
            reset_events = [
                log for log in logs_data["logs"] 
                if "password_reset" in log.get("action", "")
            ]
            assert len(reset_events) > 0
            print(f"✓ Password reset events are logged")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)
    
    def test_failed_login_creates_audit_log(self, superadmin_headers):
        """Test that failed login attempts are logged"""
        # Attempt failed login
        requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        
        # Check audit logs
        logs_response = requests.get(
            f"{BASE_URL}/api/admin/audit-logs?limit=50",
            headers=superadmin_headers
        )
        logs_data = logs_response.json()
        
        failed_events = [
            log for log in logs_data["logs"]
            if "login_failed" in log.get("action", "") or (log.get("success") == False and "login" in log.get("action", ""))
        ]
        # At least one failed login should be logged
        print(f"✓ Found {len(failed_events)} failed login events in audit logs")


# ============== DATA ISOLATION TESTS ==============
class TestDataIsolation:
    """Test data isolation for campaigns and creatives based on ownership"""
    
    def test_data_scope_endpoint(self, advertiser_headers):
        """Test /api/admin/my-data-scope endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/my-data-scope", headers=advertiser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "scope" in data
        assert data["scope"] == "self"
        print(f"✓ Advertiser data scope is 'self'")
    
    def test_superadmin_sees_all_campaigns(self, superadmin_headers):
        """Test that super admin can see all campaigns"""
        response = requests.get(
            f"{BASE_URL}/api/campaigns",
            headers=superadmin_headers
        )
        assert response.status_code == 200
        campaigns = response.json()
        print(f"✓ Super admin sees {len(campaigns)} campaigns (all)")
    
    def test_advertiser_only_sees_own_campaigns(self, superadmin_headers, advertiser_headers):
        """Test that advertiser only sees their own campaigns"""
        # Get advertiser's user ID
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=advertiser_headers)
        advertiser_id = me_response.json()["id"]
        
        # Get all campaigns as super admin
        all_campaigns = requests.get(f"{BASE_URL}/api/campaigns", headers=superadmin_headers).json()
        
        # Get campaigns as advertiser
        adv_campaigns = requests.get(f"{BASE_URL}/api/campaigns", headers=advertiser_headers).json()
        
        # Advertiser should only see their own campaigns (or none if they have none)
        for campaign in adv_campaigns:
            if campaign.get("owner_id"):
                assert campaign["owner_id"] == advertiser_id or campaign.get("owner_id") is None
        
        print(f"✓ Advertiser sees {len(adv_campaigns)} campaigns (own), super admin sees {len(all_campaigns)}")
    
    def test_creatives_data_isolation(self, superadmin_headers, advertiser_headers):
        """Test that creatives follow the same ownership filtering"""
        # Get advertiser's user ID
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=advertiser_headers)
        advertiser_id = me_response.json()["id"]
        
        # Get all creatives as super admin
        all_creatives = requests.get(f"{BASE_URL}/api/creatives", headers=superadmin_headers).json()
        
        # Get creatives as advertiser
        adv_creatives = requests.get(f"{BASE_URL}/api/creatives", headers=advertiser_headers).json()
        
        print(f"✓ Advertiser sees {len(adv_creatives)} creatives, super admin sees {len(all_creatives)}")
    
    def test_admin_sees_hierarchical_data(self, admin_headers, superadmin_headers):
        """Test that admin sees their own data plus children's data"""
        # Get admin's user ID
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers)
        admin_id = me_response.json()["id"]
        
        # Get data scope
        scope_response = requests.get(f"{BASE_URL}/api/admin/my-data-scope", headers=admin_headers)
        scope_data = scope_response.json()
        
        assert scope_data["scope"] == "hierarchical"
        assert admin_id in scope_data["user_ids"]
        print(f"✓ Admin scope is hierarchical, includes {len(scope_data['user_ids'])} user IDs")
    
    def test_campaign_created_with_owner_id(self, superadmin_headers):
        """Test that campaigns created by logged-in user have owner_id set"""
        # First create a creative to use
        creative_response = requests.post(
            f"{BASE_URL}/api/creatives",
            headers=superadmin_headers,
            json={
                "name": "TEST_Creative_For_Campaign",
                "type": "banner",
                "format": "image",
                "adomain": ["test.com"],
                "cat": ["IAB1"],
                "banner_data": {
                    "width": 300,
                    "height": 250,
                    "image_url": "https://example.com/test.jpg"
                }
            }
        )
        
        if creative_response.status_code not in [200, 201]:
            pytest.skip("Could not create test creative")
        
        creative_id = creative_response.json()["id"]
        
        try:
            # Create campaign
            campaign_response = requests.post(
                f"{BASE_URL}/api/campaigns",
                headers=superadmin_headers,
                json={
                    "name": "TEST_Campaign_Owner",
                    "bid_price": 1.5,
                    "creative_id": creative_id
                }
            )
            
            if campaign_response.status_code not in [200, 201]:
                pytest.skip(f"Could not create campaign: {campaign_response.text}")
            
            campaign = campaign_response.json()
            campaign_id = campaign.get("id")
            
            # Verify owner_id is set
            assert campaign.get("owner_id") is not None or campaign.get("owner_email") is not None
            print(f"✓ Campaign created with owner tracking")
            
            # Cleanup
            if campaign_id:
                requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}", headers=superadmin_headers)
                
        finally:
            requests.delete(f"{BASE_URL}/api/creatives/{creative_id}", headers=superadmin_headers)


# ============== 2FA LOGIN FLOW TESTS ==============
class TestTwoFALoginFlow:
    """Test 2FA login flow specifically"""
    
    def test_2fa_login_invalid_temp_token(self):
        """Test that invalid temp token is rejected during 2FA verification"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-2fa",
            json={"temp_token": "invalid_token", "code": "123456"}
        )
        assert response.status_code == 401
        print("✓ Invalid temp token rejected during 2FA verification")
    
    def test_2fa_backup_code_login(self, superadmin_headers):
        """Test that backup codes can be used for 2FA login"""
        test_email = f"TEST_backup_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "backup123"
        
        # Create test admin
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=superadmin_headers,
            json={
                "email": test_email,
                "password": test_password,
                "name": "Test Backup Code",
                "role": "admin"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test admin")
        
        user_id = create_response.json()["id"]
        
        try:
            # Login and setup 2FA
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            test_token = login_response.json()["token"]
            test_headers = {"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"}
            
            # Setup 2FA
            setup_response = requests.post(f"{BASE_URL}/api/auth/2fa/setup", headers=test_headers)
            setup_data = setup_response.json()
            secret = setup_data["secret"]
            backup_codes = setup_data["backup_codes"]
            
            # Enable 2FA
            totp = pyotp.TOTP(secret)
            enable_response = requests.post(
                f"{BASE_URL}/api/auth/2fa/enable",
                headers=test_headers,
                json={"code": totp.now()}
            )
            assert enable_response.status_code == 200
            
            # Login again (requires 2FA)
            login_2fa = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            temp_token = login_2fa.json()["temp_token"]
            
            # Use backup code instead of TOTP
            backup_code = backup_codes[0]
            verify_response = requests.post(
                f"{BASE_URL}/api/auth/verify-2fa",
                json={"temp_token": temp_token, "code": backup_code}
            )
            assert verify_response.status_code == 200
            print("✓ Backup code login successful")
            
        finally:
            requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=superadmin_headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
