# Welcome Link API Reference

## Version: 2.8.4

**Base URL:** `https://api.welcome-link.de`

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

---

## Endpoints

### 🔐 Authentication

#### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free"
  }
}
```

---

#### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free"
  }
}
```

---

#### GET /api/auth/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+49 123 456789",
  "company_name": "Example Company",
  "plan": "free",
  "created_at": "2026-01-01T00:00:00Z",
  "is_demo": false,
  "invoice_name": "Example Company GmbH",
  "invoice_address": "Musterstraße 1",
  "invoice_zip": "12345",
  "invoice_city": "Berlin",
  "invoice_country": "Deutschland",
  "invoice_vat_id": "DE123456789"
}
```

---

#### PUT /api/auth/profile
Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "+49 123 456789",
  "company_name": "Example Company",
  "invoice_name": "Example Company GmbH",
  "invoice_address": "Musterstraße 1",
  "invoice_zip": "12345",
  "invoice_city": "Berlin",
  "invoice_country": "Deutschland",
  "invoice_vat_id": "DE123456789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+49 123 456789",
    "company_name": "Example Company",
    "plan": "free",
    "invoice_name": "Example Company GmbH",
    "invoice_address": "Musterstraße 1",
    "invoice_zip": "12345",
    "invoice_city": "Berlin",
    "invoice_country": "Deutschland",
    "invoice_vat_id": "DE123456789"
  }
}
```

---

#### POST /api/auth/password-reset/request
Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset email sent"
}
```

---

#### POST /api/auth/password-reset/confirm
Confirm password reset with token.

**Request Body:**
```json
{
  "token": "reset-token",
  "new_password": "newsecurepassword"
}
```

---

#### POST /api/auth/magic-link
Request magic link for passwordless login.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

---

#### POST /api/auth/demo/init
Initialize demo account.

---

### 🏠 Properties

#### GET /api/properties
List all properties for current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "properties": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "name": "Seeblick Apartment",
      "description": "Beautiful lake view",
      "address": "Seepromenade 1, 88131 Lindau",
      "brand_color": "#F27C2C",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

---

#### POST /api/properties
Create a new property.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "My Property",
  "description": "Beautiful apartment",
  "address": "123 Main Street",
  "brand_color": "#F27C2C"
}
```

---

#### GET /api/properties/{id}
Get property by ID.

---

#### PUT /api/properties/{id}
Update property.

---

#### DELETE /api/properties/{id}
Delete property.

---

#### GET /api/properties/{id}/extras
Get extras for property.

---

### 📅 Bookings

#### GET /api/bookings
List all bookings for current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` - Filter from date (ISO 8601)
- `end_date` - Filter to date (ISO 8601)
- `status` - Filter by status (pending, confirmed, cancelled)

---

#### POST /api/bookings
Create a new booking.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "property_id": "uuid",
  "guest_name": "Max Mustermann",
  "guest_email": "max@example.com",
  "guest_phone": "+49 123 456789",
  "check_in": "2026-04-01T15:00:00Z",
  "check_out": "2026-04-07T11:00:00Z",
  "guests": 2,
  "total_price": 500.00,
  "message": "Looking forward to our stay!"
}
```

---

#### GET /api/bookings/{id}
Get booking details.

---

#### GET /api/bookings/feed
Get booking feed (calendar format).

---

### 🧹 Cleaners

#### GET /api/cleaners
List all cleaners for current user.

**Headers:** `Authorization: Bearer <token>`

---

#### POST /api/cleaners
Create a new cleaner.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Anna Rein",
  "email": "anna@example.com",
  "phone": "+49 123 456789",
  "notes": "Available Monday-Friday"
}
```

---

#### PUT /api/cleaners/{id}
Update cleaner.

---

#### DELETE /api/cleaners/{id}
Delete cleaner.

---

#### POST /api/properties/{id}/cleaners
Assign cleaner to property.

**Request Body:**
```json
{
  "cleaner_id": "uuid",
  "notify_hours_before": 24
}
```

---

#### DELETE /api/properties/{id}/cleaners/{cleaner_id}
Remove cleaner from property.

---

#### GET /api/properties/{id}/cleaners
Get cleaners for property.

---

### 📊 Guestview

#### POST /api/guestview-token
Generate guestview token.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "property_id": "uuid"
}
```

---

#### GET /api/guestview/{token}
Get guestview by token (public).

---

### 💳 Subscriptions

#### POST /api/subscription/create
Create Stripe checkout session.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "plan": "starter",
  "billing_cycle": "monthly"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_..."
}
```

---

#### POST /api/subscription/portal
Get Stripe customer portal URL.

**Headers:** `Authorization: Bearer <token>`

---

#### GET /api/subscription/status
Get current subscription status.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "plan": "starter",
  "status": "active",
  "current_period_end": "2026-04-30T23:59:59Z",
  "cancel_at_period_end": false
}
```

---

### 🪝 Webhooks

#### POST /api/webhooks/stripe
Handle Stripe webhook events.

**Events:**
- `checkout.session.completed` - Activate plan
- `customer.subscription.updated` - Update plan
- `customer.subscription.deleted` - Downgrade to free

---

#### POST /api/webhooks/paypal
Handle PayPal webhook events.

---

### ⏰ Cron Jobs

#### POST /api/cron/booking-reminders
Send booking reminder emails.

---

#### POST /api/cron/guest-welcome
Send guest welcome emails.

---

#### POST /api/cron/checkout-followup
Send checkout followup emails.

---

#### POST /api/cron/cleaning-notifications
Send cleaning notifications to assigned cleaners.

---

### 🔧 Admin Endpoints

#### POST /api/admin/login
Admin login.

---

#### GET /api/admin/users
List all users (admin only).

---

#### PATCH /api/admin/users/{id}/plan
Update user plan (admin only).

---

#### GET /api/admin/stats
Get global statistics (admin only).

---

#### GET /api/admin/export/bookings
Export bookings as CSV (admin only).

---

### 📈 Stats

#### GET /api/stats/global
Get global statistics.

---

#### GET /api/stats/bookings
Get booking statistics.

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/auth/register` | 5/minute |
| `/api/auth/login` | 10/minute |
| `/api/auth/magic-link` | 3/minute |
| All other endpoints | 100/minute |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

---

## Postman Collection

Import the following collection into Postman:

```json
{
  "info": {
    "name": "Welcome Link API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.welcome-link.de"
    },
    {
      "key": "token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\"email\": \"demo@welcome-link.de\", \"password\": \"Demo123!\"}"
            },
            "url": "{{base_url}}/api/auth/login"
          }
        },
        {
          "name": "Get Profile",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
            "url": "{{base_url}}/api/auth/me"
          }
        }
      ]
    }
  ]
}
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
const API_URL = 'https://api.welcome-link.de';

// Login
const login = async (email: string, password: string) => {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data.user;
};

// Get Profile
const getProfile = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};

// Update Profile
const updateProfile = async (data: object) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/auth/profile`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

### Python

```python
import requests

API_URL = 'https://api.welcome-link.de'

class WelcomeLinkAPI:
    def __init__(self, token=None):
        self.token = token
    
    def login(self, email, password):
        response = requests.post(
            f'{API_URL}/api/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        self.token = data['token']
        return data['user']
    
    def get_profile(self):
        response = requests.get(
            f'{API_URL}/api/auth/me',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        return response.json()
    
    def update_profile(self, data):
        response = requests.put(
            f'{API_URL}/api/auth/profile',
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            json=data
        )
        return response.json()
```

---

## Changelog

### v2.8.4 (18.03.2026)
- Added complete profile API with all fields
- Fixed PUT /api/auth/profile to save data
- Added phone, company_name, plan to User model

### v2.8.3 (18.03.2026)
- Fixed Cleaner models import error
- Added Cleaner and PropertyCleaner models

### v2.8.2 (17.03.2026)
- Made psutil optional for deployment

### v2.8.1 (16.03.2026)
- Fixed welcome email on registration

### v2.8.0 (16.03.2026)
- Added Cleaner management
- Added cleaning notification endpoints

### v2.7.3 (12.03.2026)
- Added performance monitoring
- Enhanced health check with system metrics

### v2.7.2 (07.03.2026)
- Improved Stripe webhook security
- Activated real booking queries

### v2.7.1 (07.03.2026)
- Email templates
- Cron jobs
- Webhooks