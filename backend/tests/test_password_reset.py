"""
Tests for Password Reset API Endpoints
Validation tests for password reset and magic link endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

class TestPasswordResetValidation:
    """Password Reset Validation Tests - Tests for input validation"""
    
    def test_request_password_reset_invalid_email_format(self):
        """Test password reset request with invalid email format"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": "invalid-email"}
        )
        # Should fail validation (not a valid email)
        assert response.status_code == 422
    
    def test_confirm_password_reset_with_token(self):
        """Test password reset confirmation endpoint exists"""
        # Just verify the endpoint accepts the request format
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={"token": "test-token-123", "new_password": "newpassword123"}
        )
        # Should fail because token doesn't exist (not validation error)
        assert response.status_code in [400, 404]


class TestMagicLinkValidation:
    """Magic Link Validation Tests - Tests for input validation"""
    
    def test_request_magic_link_invalid_email_format(self):
        """Test magic link request with invalid email format"""
        response = client.post(
            "/api/auth/magic-link",
            json={"email": "not-an-email"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_request_magic_link_missing_email(self):
        """Test magic link request without email"""
        response = client.post(
            "/api/auth/magic-link",
            json={}
        )
        assert response.status_code == 422  # Validation error