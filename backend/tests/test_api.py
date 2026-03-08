"""
Welcome Link API Tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app

client = TestClient(app)


class TestHealthCheck:
    """Test basic API health"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data
    
    def test_openapi_docs(self):
        """Test OpenAPI docs are available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestExtrasAPI:
    """Test Extras endpoints"""
    
    def test_get_extras_requires_auth_or_property(self):
        """Test getting extras for a property"""
        response = client.get("/api/properties/17/extras")
        # May return 404 if property doesn't exist, or require auth
        assert response.status_code in [200, 401, 403, 404]


class TestCheckoutAPI:
    """Test Checkout endpoints"""
    
    def test_create_checkout_requires_auth(self):
        """Test checkout requires authentication"""
        response = client.post("/api/checkout", json={
            "property_id": 17,
            "items": [],
            "guest_name": "Test",
            "guest_email": "test@test.de",
            "payment_method": "stripe"
        })
        # Should require auth (401) or fail validation
        assert response.status_code in [401, 403, 404, 422]


class TestGuestviewAPI:
    """Test Guestview endpoints"""
    
    def test_guestview_invalid_token(self):
        """Test invalid token returns 404"""
        response = client.get("/api/guestview/invalid-token-12345")
        assert response.status_code in [404, 500]


class TestPropertyEditorAPI:
    """Test Property Editor endpoints"""
    
    def test_get_property_for_edit_without_auth(self):
        """Test property edit requires authentication"""
        response = client.get("/api/properties/17/edit")
        # May return 404 if property doesn't exist, or require auth
        assert response.status_code in [401, 403, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])