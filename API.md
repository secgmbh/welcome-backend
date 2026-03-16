# Welcome Link API Documentation

## Base URL
```
Production: https://api.welcome-link.de
Development: http://localhost:8000
```

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "phone": "+49123456789",      // optional
  "company_name": "Hotel ABC"    // optional
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free",
    "max_properties": 1,
    "created_at": "2026-03-16T12:00:00Z"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

#### Update Profile
```http
PUT /api/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Name",
  "phone": "+49123456789",
  "company_name": "New Company"
}
```

#### Password Reset Request
```http
POST /api/auth/password-reset/request
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Password Reset Confirm
```http
POST /api/auth/password-reset/confirm
Content-Type: application/json

{
  "token": "reset_token",
  "new_password": "newpassword123"
}
```

---

### Properties

#### List Properties
```http
GET /api/properties
Authorization: Bearer <token>
```

#### Create Property
```http
POST /api/properties
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Apartment Berlin",
  "address": "Hauptstraße 123",
  "city": "Berlin",
  "description": "Schönes Apartment im Zentrum",
  "max_guests": 4
}
```

#### Get Property
```http
GET /api/properties/{id}
Authorization: Bearer <token>
```

#### Update Property
```http
PUT /api/properties/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name"
}
```

#### Delete Property
```http
DELETE /api/properties/{id}
Authorization: Bearer <token>
```

---

### Bookings

#### List Bookings
```http
GET /api/bookings
Authorization: Bearer <token>
```

#### Create Booking
```http
POST /api/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": "uuid",
  "guest_name": "Max Mustermann",
  "guest_email": "max@example.com",
  "check_in": "2026-04-01",
  "check_out": "2026-04-05",
  "guests": 2
}
```

#### Get Booking
```http
GET /api/bookings/{id}
Authorization: Bearer <token>
```

---

### Subscriptions

#### Create Subscription
```http
POST /api/subscription/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "starter"  // free, starter, pro, enterprise
}
```

**Response:**
```json
{
  "url": "https://checkout.stripe.com/..."
}
```

**Demo Mode (without Stripe):**
```json
{
  "url": "https://www.welcome-link.de/checkout/demo?plan=starter"
}
```

#### Get Subscription Status
```http
GET /api/subscription/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "plan": "starter",
  "max_properties": 3,
  "trial_ends_at": null,
  "is_active": true
}
```

#### Customer Portal
```http
POST /api/subscription/portal
Authorization: Bearer <token>
```

---

### Guest View

#### Get Guest View
```http
GET /api/guestview/{token}
```

No authentication required - public endpoint for guests.

---

### Admin Endpoints

#### List Users (Admin)
```http
GET /api/admin/users
Authorization: Bearer <admin_token>
```

#### Update User Plan (Admin)
```http
PATCH /api/admin/users/{id}/plan
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "plan": "pro"
}
```

---

### Webhooks

#### Stripe Webhook
```http
POST /api/webhooks/stripe
Stripe-Signature: <signature>
Content-Type: application/json

{
  "type": "checkout.session.completed",
  "data": { ... }
}
```

#### PayPal Webhook
```http
POST /api/webhooks/paypal
Content-Type: application/json

{
  "event_type": "PAYMENT.CAPTURE.COMPLETED",
  ...
}
```

---

### Cron Jobs

#### Booking Reminders
```http
POST /api/cron/booking-reminders
X-Cron-Key: <cron_key>
```

#### Guest Welcome
```http
POST /api/cron/guest-welcome
X-Cron-Key: <cron_key>
```

#### Checkout Followup
```http
POST /api/cron/checkout-followup
X-Cron-Key: <cron_key>
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message in German or English"
}
```

### Common HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Token missing/invalid |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Server Error |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/auth/register` | 5/minute |
| `/api/auth/login` | 10/minute |
| `/api/auth/magic-link` | 3/minute |
| Default | 100/minute |

---

## Plan Limits

| Plan | Price | Properties | Features |
|------|-------|------------|----------|
| Free | €0 | 1 | Basic features |
| Starter | €9/mo | 3 | + Extras, QR-Codes |
| Pro | €29/mo | 10 | + Analytics, API |
| Enterprise | Custom | Unlimited | + White-Label, Support |

---

## Demo Credentials

```
Email: demo@welcome-link.de
Password: Demo123!
```

Note: Demo account has no admin access.

---

## Postman Collection

Import this collection to test the API:

```json
{
  "info": {
    "name": "Welcome Link API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "https://api.welcome-link.de" },
    { "key": "token", "value": "" }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/auth/register",
            "header": [{ "key": "Content-Type", "value": "application/json" }],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test1234!\",\n  \"name\": \"Test User\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "event": [{
            "listen": "test",
            "script": {
              "exec": [
                "var jsonData = JSON.parse(responseBody);",
                "pm.collectionVariables.set('token', jsonData.token);"
              ]
            }
          }],
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/auth/login",
            "header": [{ "key": "Content-Type", "value": "application/json" }],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test1234!\"\n}"
            }
          }
        },
        {
          "name": "Get Me",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/auth/me",
            "header": [{ "key": "Authorization", "value": "Bearer {{token}}" }]
          }
        }
      ]
    },
    {
      "name": "Properties",
      "item": [
        {
          "name": "List Properties",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/properties",
            "header": [{ "key": "Authorization", "value": "Bearer {{token}}" }]
          }
        },
        {
          "name": "Create Property",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/properties",
            "header": [
              { "key": "Authorization", "value": "Bearer {{token}}" },
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"My Property\",\n  \"address\": \"Street 1\",\n  \"city\": \"Berlin\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Subscription",
      "item": [
        {
          "name": "Get Status",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/subscription/status",
            "header": [{ "key": "Authorization", "value": "Bearer {{token}}" }]
          }
        },
        {
          "name": "Create Subscription",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/subscription/create",
            "header": [
              { "key": "Authorization", "value": "Bearer {{token}}" },
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"plan\": \"starter\"\n}"
            }
          }
        }
      ]
    }
  ]
}
```