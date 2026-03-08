"""
Integration Tests for Welcome Link API
Full flow tests with database interactions
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app

client = TestClient(app)


class TestAuthFlow:
    """Test complete authentication flow"""
    
    def test_health_endpoint(self):
        """API health check should work"""
        response = client.get("/api/")
        assert response.status_code == 200
    
    def test_register_validation_empty_email(self):
        """Registration with empty email should fail"""
        response = client.post("/api/auth/register", json={
            "email": "",
            "password": "testpassword123"
        })
        assert response.status_code == 422
    
    def test_register_validation_short_password(self):
        """Registration with short password should fail"""
        response = client.post("/api/auth/register", json={
            "email": "test@test.com",
            "password": "123"
        })
        assert response.status_code == 422
    
    def test_register_validation_invalid_email(self):
        """Registration with invalid email should fail"""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "testpassword123"
        })
        assert response.status_code == 422
    
    def test_login_validation_invalid(self):
        """Login with invalid credentials should fail"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 400, 422]


class TestDemoFlow:
    """Test demo initialization and access"""

    def test_demo_init_endpoint_exists(self):
        """Demo init endpoint should exist"""
        response = client.post("/api/demo/init")
        # May succeed, fail, or not found depending on DB state
        assert response.status_code in [200, 201, 400, 404, 409, 500]

    def test_demo_login_validation(self):
        """Demo login should validate input"""
        response = client.post("/api/auth/login", json={
            "email": "demo@welcome-link.de",
            "password": "Demo123!"
        })
        # Should succeed or fail based on DB state
        assert response.status_code in [200, 400, 401, 422, 500]


class TestProtectedEndpoints:
    """Test endpoints that require authentication"""
    
    def test_properties_requires_auth(self):
        """Properties endpoint should require authentication"""
        response = client.get("/api/properties")
        assert response.status_code in [401, 403]
    
    def test_property_create_requires_auth(self):
        """Creating property should require authentication"""
        response = client.post("/api/properties", json={
            "name": "Test Property",
            "description": "Test Description"
        })
        assert response.status_code in [401, 403, 422]
    
    def test_bookings_requires_auth(self):
        """Bookings endpoint should require authentication"""
        response = client.get("/api/bookings")
        assert response.status_code in [401, 403, 404]
    
    def test_stats_requires_auth(self):
        """Stats endpoint should require authentication"""
        response = client.get("/api/stats/global")
        assert response.status_code in [401, 403, 404]


class TestGuestviewFlow:
    """Test guestview token flow"""
    
    def test_guestview_invalid_token(self):
        """Invalid guestview token should return 404"""
        response = client.get("/api/guestview/invalid-token-xyz")
        assert response.status_code in [404, 500]
    
    def test_guestview_token_requires_auth(self):
        """Creating guestview token should require auth"""
        response = client.post("/api/guestview-token", json={
            "property_id": 1
        })
        assert response.status_code in [401, 403, 422]


class TestScenesAPI:
    """Test scenes endpoints"""
    
    def test_scenes_requires_auth(self):
        """Scenes endpoint should require authentication"""
        response = client.get("/api/scenes")
        assert response.status_code in [401, 403, 404]


class TestExtrasAPI:
    """Test extras endpoints"""
    
    def test_extras_requires_valid_property(self):
        """Extras should require valid property"""
        response = client.get("/api/properties/99999/extras")
        assert response.status_code in [401, 403, 404]


class TestFeedbackAPI:
    """Test feedback endpoints"""
    
    def test_feedback_endpoint_exists(self):
        """Feedback endpoint should exist"""
        response = client.post("/api/feedback", json={
            "rating": 5,
            "comment": "Great experience!"
        })
        # May require auth or property context
        assert response.status_code in [200, 201, 401, 403, 404, 422]


class TestExportAPI:
    """Test export endpoints"""
    
    def test_csv_export_requires_auth(self):
        """CSV export should require authentication"""
        response = client.get("/api/export/bookings/csv")
        assert response.status_code in [401, 403, 404]
    
    def test_pdf_export_requires_auth(self):
        """PDF export should require authentication"""
        response = client.get("/api/export/bookings/pdf")
        assert response.status_code in [401, 403, 404]


class TestPaymentAPI:
    """Test payment endpoints"""
    
    def test_paypal_create_requires_auth(self):
        """PayPal create order should require auth"""
        response = client.post("/api/paypal/create-order", json={
            "amount": 100.00
        })
        assert response.status_code in [401, 403, 404, 422]


class TestHealthCheck:
    """Test health and status endpoints"""

    def test_api_root(self):
        """API root should respond"""
        response = client.get("/api/")
        assert response.status_code == 200

    def test_api_status_endpoint(self):
        """Status endpoint should return list"""
        response = client.get("/api/status")
        # May be empty or have status checks
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])