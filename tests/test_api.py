"""
Welcome Link Backend Tests
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server import app, get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
        assert data["success"] is True
    
    def test_register_duplicate_email(self):
        """Test duplicate email registration fails"""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        # Second registration with same email
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test456!",
                "name": "Another User"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self):
        """Test successful login"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword!"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user with token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!"
            }
        )
        token = login_response.json()["token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"


class TestProperties:
    """Property endpoints tests"""
    
    @pytest.fixture
    def auth_header(self):
        """Get auth header for authenticated requests"""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!"
            }
        )
        token = login_response.json()["token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_property(self, auth_header):
        """Test property creation"""
        response = client.post(
            "/api/properties",
            json={
                "name": "Test Property",
                "description": "A test property",
                "address": "Test Street 1, 12345 Berlin"
            },
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Property"
    
    def test_list_properties(self, auth_header):
        """Test listing user properties"""
        # Create property
        client.post(
            "/api/properties",
            json={
                "name": "Test Property",
                "description": "A test property",
                "address": "Test Street 1, 12345 Berlin"
            },
            headers=auth_header
        )
        
        # List properties
        response = client.get("/api/properties", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/properties")
        assert response.status_code == 401


class TestExtras:
    """Extras endpoints tests"""
    
    @pytest.fixture
    def setup(self):
        """Setup user and property"""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User"
            }
        )
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!"
            }
        )
        token = login_response.json()["token"]
        auth_header = {"Authorization": f"Bearer {token}"}
        
        # Create property
        property_response = client.post(
            "/api/properties",
            json={
                "name": "Test Property",
                "description": "A test property",
                "address": "Test Street 1"
            },
            headers=auth_header
        )
        property_id = property_response.json()["id"]
        
        return auth_header, property_id
    
    def test_create_extra(self, setup):
        """Test creating an extra"""
        auth_header, property_id = setup
        
        response = client.post(
            f"/api/properties/{property_id}/extras",
            json={
                "name": "Frühstück",
                "description": "Reichhaltiges Frühstück",
                "price": 15.00,
                "category": "food"
            },
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Frühstück"
        assert data["price"] == 15.00
    
    def test_list_extras(self, setup):
        """Test listing extras"""
        auth_header, property_id = setup
        
        # Create extra
        client.post(
            f"/api/properties/{property_id}/extras",
            json={
                "name": "Frühstück",
                "description": "Reichhaltiges Frühstück",
                "price": 15.00,
                "category": "food"
            },
            headers=auth_header
        )
        
        # List extras
        response = client.get(
            f"/api/properties/{property_id}/extras",
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert "extras" in data
        assert len(data["extras"]) >= 1


class TestHealth:
    """Health check tests"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])