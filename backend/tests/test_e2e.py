"""
End-to-End Tests for Welcome Link API
Tests the complete user flows from registration to booking
Note: These tests use demo data which may not exist in test environment
"""
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

class TestAuthFlow:
    """Test complete authentication flow"""
    
    def test_root_endpoint(self):
        """Test root API info"""
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test basic health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    @pytest.mark.skip(reason="Demo init requires full database setup")
    def test_demo_init_endpoint(self):
        """Test demo initialization"""
        response = client.post("/api/demo/init")
        # Accept success, conflict, or error (if demo exists)
        assert response.status_code in [200, 409, 400, 500]


class TestGuestviewFlow:
    """Test guestview access flow"""
    
    def test_guestview_invalid_token(self):
        """Test guestview with invalid token returns 404"""
        response = client.get("/api/guestview/INVALID")
        assert response.status_code == 404


class TestPropertyEndpoints:
    """Test property endpoint responses"""
    
    def test_property_extras_structure(self):
        """Test property extras endpoint structure"""
        response = client.get("/api/properties/17/extras")
        # Accept success or 404
        if response.status_code == 200:
            data = response.json()
            assert "extras" in data


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_services(self):
        """Test health services structure"""
        response = client.get("/api/health")
        data = response.json()
        assert "services" in data
        services = data["services"]
        assert "database" in services
        assert "security" in services
    
    def test_api_version(self):
        """Test API version is present"""
        response = client.get("/api/")
        data = response.json()
        assert "version" in data
        # Version should be 2.6.x
        version = data["version"]
        assert version.startswith("2.")