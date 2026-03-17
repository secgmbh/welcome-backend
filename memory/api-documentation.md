# Welcome Link API Documentation

## Base URL
```
https://api.welcome-link.de
```

## Authentication
Most endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

Get token via `/api/auth/login`.

---

## Public Endpoints

### GET /api/public/properties/:public_id
Get property data for guestview page.

**Response:**
```json
{
  "id": 17,
  "name": "Seeblick Apartment",
  "description": "Wunderschönes Apartment mit Seeblick",
  "address": "Seestraße 42, 83242 Bernau",
  "wifi": {
    "name": "Seeblick-Guest",
    "password": "Sommer2024!"
  },
  "keysafe": {
    "location": "Links neben der Eingangstür",
    "code": "4287",
    "instructions": "Code eingeben und nach unten ziehen"
  },
  "checkin_time": "15:00",
  "checkout_time": "11:00",
  "host": {
    "phone": "+49 8051 123456",
    "email": "host@example.com",
    "whatsapp": "+49 170 1234567"
  }
}
```

---

## Authentication Endpoints

### POST /api/auth/register
Register a new user.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "Max Mustermann"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully"
}
```

### POST /api/auth/login
Login and get JWT token.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "Max Mustermann"
  }
}
```

### GET /api/auth/me
Get current user data (requires auth).

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Max Mustermann"
}
```

---

## Properties Endpoints

### GET /api/properties
List user's properties (requires auth).

### POST /api/properties
Create a new property (requires auth).

### GET /api/properties/:id
Get property by ID (requires auth).

### PUT /api/properties/:id
Update property (requires auth).

### DELETE /api/properties/:id
Delete property (requires auth).

---

## Extras Endpoints

### GET /api/properties/:property_id/extras
Get all extras for a property.

**Response:**
```json
{
  "extras": [
    {
      "id": "uuid",
      "name": "Frühstück",
      "description": "Reichhaltiges Frühstück",
      "price": 15.00,
      "category": "food",
      "is_active": true
    }
  ]
}
```

### POST /api/properties/:property_id/extras
Create a new extra (requires auth).

**Body:**
```json
{
  "name": "Frühstück",
  "description": "Reichhaltiges Frühstück",
  "price": 15.00,
  "category": "food"
}
```

---

## Checkout Endpoints

### POST /api/checkout
Create a new checkout order.

**Body:**
```json
{
  "property_id": 17,
  "items": [
    { "extra_id": "uuid", "quantity": 2 }
  ],
  "guest_name": "Max Mustermann",
  "guest_email": "max@example.com",
  "payment_method": "stripe"
}
```

**Response:**
```json
{
  "success": true,
  "checkout_id": "uuid",
  "total": 30.00
}
```

### GET /api/checkout/:id/invoice
Get PDF invoice for checkout.

**Response:** PDF file download.

---

## Payment Endpoints

### POST /api/payment/stripe/create-session
Create Stripe checkout session.

**Body:**
```json
{
  "checkout_id": "uuid",
  "success_url": "https://example.com/success",
  "cancel_url": "https://example.com/cancel"
}
```

### POST /api/payment/paypal/create-order
Create PayPal order.

### POST /api/payment/stripe/webhook
Stripe webhook endpoint (public).

---

## Debug Endpoints (Development)

### POST /api/debug/migrate-extras
Create extras table.

### POST /api/debug/migrate-checkouts
Create checkouts table.

### POST /api/debug/migrate-qr-scans
Create qr_scans table.

### POST /api/debug/seed-extras/:property_id
Seed demo extras for a property (requires auth).

---

## Rate Limits

| Endpoint Type | Rate Limit |
|--------------|------------|
| Public | 60/minute |
| Authenticated | 100/minute |
| Checkout | 10/minute |

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (no permission)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

---

## Demo Credentials

For testing:
- **Email:** demo@welcome-link.de
- **Password:** Demo123!
- **Property ID:** 17
- **Public ID:** QEJHEXP1QF