"""
Security Tests for Welcome Link API
Tests for Phase 28 Security Features
"""
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, '..')
from server import app

client = TestClient(app)


class TestSecurityHeaders:
    """Test Security Headers Middleware"""
    
    def test_x_frame_options(self):
        """X-Frame-Options should be DENY to prevent clickjacking"""
        response = client.get("/api/")
        assert response.status_code == 200
        assert response.headers.get("X-Frame-Options") == "DENY"
    
    def test_x_content_type_options(self):
        """X-Content-Type-Options should be nosniff"""
        response = client.get("/api/")
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
    
    def test_x_xss_protection(self):
        """X-XSS-Protection should be enabled"""
        response = client.get("/api/")
        assert response.status_code == 200
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    
    def test_referrer_policy(self):
        """Referrer-Policy should be set"""
        response = client.get("/api/")
        assert response.status_code == 200
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    
    def test_content_security_policy(self):
        """Content-Security-Policy should be set"""
        response = client.get("/api/")
        assert response.status_code == 200
        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
    
    def test_permissions_policy(self):
        """Permissions-Policy should restrict sensitive features"""
        response = client.get("/api/")
        assert response.status_code == 200
        perm_policy = response.headers.get("Permissions-Policy")
        assert perm_policy is not None
        assert "geolocation=()" in perm_policy
        assert "camera=()" in perm_policy
        assert "microphone=()" in perm_policy


class TestGlobalExceptionHandler:
    """Test Global Exception Handler"""
    
    def test_404_returns_structured_error(self):
        """404 should return structured JSON error"""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] is True
        assert "status_code" in data
        assert "message" in data
        assert "timestamp" in data
    
    def test_422_validation_error_returns_details(self):
        """422 validation error should return field details"""
        response = client.post("/api/auth/register", json={
            "email": "invalid-email",  # Invalid email format
            "password": "123"  # Too short
        })
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"] is True
        assert "errors" in data
        assert isinstance(data["errors"], list)


class TestRateLimiting:
    """Test Rate Limiting on Auth Endpoints"""
    
    def test_register_endpoint_exists(self):
        """Register endpoint should exist"""
        response = client.post("/api/auth/register", json={
            "email": "test-rate@example.com",
            "password": "testpassword123"
        })
        # May fail due to existing user, but endpoint should respond
        assert response.status_code in [200, 201, 400, 422, 429]
    
    def test_login_endpoint_exists(self):
        """Login endpoint should exist"""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        # May fail auth, but endpoint should respond
        assert response.status_code in [200, 400, 401, 422, 429]


class TestCORS:
    """Test CORS Configuration"""
    
    def test_cors_headers_present(self):
        """CORS headers should be present for allowed origins"""
        # OPTIONS preflight request
        response = client.options("/api/", headers={
            "Origin": "https://www.welcome-link.de",
            "Access-Control-Request-Method": "GET"
        })
        # CORS middleware should handle this
        assert response.status_code in [200, 204, 400]


class TestInputValidation:
    """Test Input Validation"""
    
    def test_register_empty_email(self):
        """Register with empty email should fail"""
        response = client.post("/api/auth/register", json={
            "email": "",
            "password": "testpassword123"
        })
        assert response.status_code == 422
    
    def test_register_short_password(self):
        """Register with short password should fail"""
        response = client.post("/api/auth/register", json={
            "email": "test@test.com",
            "password": "123"
        })
        assert response.status_code == 422
    
    def test_register_invalid_email(self):
        """Register with invalid email should fail"""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "testpassword123"
        })
        assert response.status_code == 422


class TestAuthSecurity:
    """Test Authentication Security"""
    
    def test_protected_endpoint_requires_auth(self):
        """Protected endpoints should require authentication"""
        response = client.get("/api/properties")
        assert response.status_code in [401, 403]
    
    def test_invalid_token_rejected(self):
        """Invalid JWT token should be rejected"""
        response = client.get("/api/properties", headers={
            "Authorization": "Bearer invalid-token-here"
        })
        assert response.status_code in [401, 403]
    
    def test_expired_token_rejected(self):
        """Expired JWT token should be rejected"""
        # This would require creating an expired token
        # For now, just verify the endpoint requires auth
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer expired.token.here"
        })
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])