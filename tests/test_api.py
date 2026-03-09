"""
Welcome Link Backend Tests
Run with: pytest tests/ -v
"""

import pytest
import sys
import os
from pathlib import Path

# Set test database BEFORE any backend imports
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-minimum-32-characters'

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# NOW import after env vars are set
from fastapi.testclient import TestClient
from database import init_db, Base, engine
from server import app

# Initialize test database
init_db()

client = TestClient(app)


class TestHealth:
    """Health check tests"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]


class TestAuth:
    """Authentication endpoints tests"""

    def test_register_user(self):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_register_duplicate_email(self):
        """Test duplicate email registration"""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "email": "duplicate2@example.com",
                "password": "Test123!",
                "name": "First User"
            }
        )
        # Second registration with same email
        response = client.post(
            "/api/auth/register",
            json={
                "email": "duplicate2@example.com",
                "password": "Test123!",
                "name": "Second User"
            }
        )
        assert response.status_code == 400

    def test_login_success(self):
        """Test successful login"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "login2@example.com",
                "password": "Test123!",
                "name": "Login User"
            }
        )
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "login2@example.com",
                "password": "Test123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

    def test_get_current_user(self):
        """Test getting current user"""
        # Register and login
        reg_response = client.post(
            "/api/auth/register",
            json={
                "email": "current2@example.com",
                "password": "Test123!",
                "name": "Current User"
            }
        )
        token = reg_response.json()["token"]
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current2@example.com"


class TestProperties:
    """Property endpoints tests"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Setup authenticated user"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "prop2@example.com",
                "password": "Test123!",
                "name": "Property User"
            }
        )
        self.token = response.json()["token"]

    def test_create_property(self):
        """Test creating a property"""
        response = client.post(
            "/api/properties",
            json={
                "name": "Test Property",
                "address": "Test Address 123",
                "city": "Test City"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Property"

    def test_list_properties(self):
        """Test listing properties"""
        # Create a property first
        client.post(
            "/api/properties",
            json={
                "name": "List Property",
                "address": "List Address 123",
                "city": "List City"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        # List properties
        response = client.get(
            "/api/properties",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestExtras:
    """Extras endpoints tests"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Setup authenticated user and property"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "extra2@example.com",
                "password": "Test123!",
                "name": "Extra User"
            }
        )
        self.token = response.json()["token"]
        
        # Create a property
        prop_response = client.post(
            "/api/properties",
            json={
                "name": "Extra Property",
                "address": "Extra Address 123",
                "city": "Extra City"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.property_id = prop_response.json()["id"]

    def test_create_extra(self):
        """Test creating an extra"""
        response = client.post(
            f"/api/properties/{self.property_id}/extras",
            json={
                "name": "Test Extra",
                "price": 10.0,
                "description": "Test Description"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200

    def test_list_extras(self):
        """Test listing extras"""
        # Create an extra first
        client.post(
            f"/api/properties/{self.property_id}/extras",
            json={
                "name": "List Extra",
                "price": 15.0,
                "description": "List Description"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        # List extras
        response = client.get(
            f"/api/properties/{self.property_id}/extras",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200