# Welcome Link API Documentation

## Overview

Welcome Link is a digital guest guide platform for vacation rentals. This API provides endpoints for property management, guest views, bookings, extras, and analytics.

**Base URL:** `https://api.welcome-link.de`

**Version:** 2.5.0

---

## Authentication

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "demo@welcome-link.de",
  "password": "Demo123!"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "demo@welcome-link.de",
    "name": "Demo Benutzer"
  }
}
```

### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "new@user.de",
  "password": "SecurePass123",
  "name": "Max Mustermann"
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

---

## Guestview (Public)

### Get Guestview by Token

No authentication required. Access via unique token.

```http
GET /api/guestview/{token}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "name": "Host Name",
    "email": "host@example.com"
  },
  "properties": [{
    "id": "17",
    "name": "Ferienwohnung Seeblick",
    "wifi_name": "Guest-WiFi",
    "wifi_password": "password123",
    "checkin_time": "15:00",
    "checkout_time": "11:00"
  }],
  "extras": [...]
}
```

---

## Properties

### List Properties

```http
GET /api/properties
Authorization: Bearer <token>
```

### Create Property

```http
POST /api/properties
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Apartment",
  "description": "Beautiful apartment in the city center",
  "address": "Main Street 123, 12345 Berlin"
}
```

### Get Property

```http
GET /api/properties/{property_id}
Authorization: Bearer <token>
```

### Update Property

```http
PUT /api/properties/{property_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "wifi_name": "New-WiFi",
  "wifi_password": "newpassword"
}
```

### Delete Property

```http
DELETE /api/properties/{property_id}
Authorization: Bearer <token>
```

---

## Extras

### Get Extras for Property

```http
GET /api/properties/{property_id}/extras
```

### Create Extra

```http
POST /api/properties/{property_id}/extras
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Frühstück",
  "description": "Reichhaltiges Frühstück",
  "price": 15.00,
  "category": "food"
}
```

---

## Bookings

### List Bookings

```http
GET /api/bookings
Authorization: Bearer <token>
```

### Create Booking

```http
POST /api/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": "17",
  "guest_name": "Max Mustermann",
  "guest_email": "max@example.com",
  "checkin_date": "2026-03-10",
  "checkout_date": "2026-03-15"
}
```

---

## Scenes (Info Scenes)

### List Scenes

```http
GET /api/scenes
Authorization: Bearer <token>
```

### Create Scene

```http
POST /api/scenes
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": "17",
  "title": "Willkommen",
  "content": "Herzlich willkommen in unserer Ferienwohnung!",
  "order": 1
}
```

---

## Statistics & Analytics

### Global Stats

```http
GET /api/stats/global
Authorization: Bearer <token>
```

### Host Stats

```http
GET /api/stats/host/{host_id}
Authorization: Bearer <token>
```

### Filter Bookings

```http
POST /api/stats/booking/filter
Authorization: Bearer <token>
Content-Type: application/json

{
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "status": "completed"
}
```

---

## Export

### CSV Export

```http
GET /api/export/bookings/csv
Authorization: Bearer <token>
```

### PDF Export

```http
GET /api/export/bookings/pdf
Authorization: Bearer <token>
```

---

## Payment

### PayPal Create Order

```http
POST /api/paypal/create-order
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100.00
}
```

### PayPal Capture Order

```http
POST /api/paypal/capture-order
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": "paypal-order-id"
}
```

---

## Admin Endpoints

### Get All Users (Admin)

```http
GET /api/admin/users
Authorization: Bearer <admin-token>
```

### Get Admin Stats

```http
GET /api/admin/stats
Authorization: Bearer <admin-token>
```

### Bookings Live Feed

```http
GET /api/admin/bookings/feed
Authorization: Bearer <admin-token>
```

---

## Health Check

### API Health

```http
GET /api/
```

**Response:**
```json
{
  "message": "Welcome Link API",
  "version": "2.5.0",
  "status": "healthy"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests (Rate Limited) |
| 500 | Internal Server Error |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/auth/register` | 5/minute |
| `/api/auth/login` | 10/minute |
| `/api/auth/magic-link` | 3/minute |

---

## Security Headers

All responses include these security headers:

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## Demo Credentials

For testing, use these demo credentials:

- **Email:** `demo@welcome-link.de`
- **Password:** `Demo123!`

---

## Support

- **Documentation:** https://docs.welcome-link.de
- **API Status:** https://status.welcome-link.de
- **Contact:** support@welcome-link.de