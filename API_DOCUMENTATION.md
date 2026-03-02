# Welcome Link API Documentation

## Base URL
- Production: `https://api.welcome-link.de`
- Development: `http://localhost:8000`

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Auth Endpoints

### Register User
```
POST /api/auth/register
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name",
  "invoice_name": "Company GmbH",
  "invoice_address": "Street 123",
  "invoice_zip": "12345",
  "invoice_city": "City",
  "invoice_country": "Germany",
  "invoice_vat_id": "DE123456789"
}
```

### Login
```
POST /api/auth/login
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Get Current User
```
GET /api/auth/me
```
**Headers:** `Authorization: Bearer <token>`

### Magic Link
```
POST /api/auth/magic-link
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

### Verify Email
```
POST /api/auth/verify-email
```
**Body:**
```json
{
  "token": "verification_token"
}
```

---

## Properties Endpoints

### List Properties
```
GET /api/properties
```
**Headers:** `Authorization: Bearer <token>`

### Get Property
```
GET /api/properties/{id}
```
**Headers:** `Authorization: Bearer <token>`

### Create Property
```
POST /api/properties
```
**Body:**
```json
{
  "name": "Hotel Alpenblick",
  "description": "Beautiful mountain hotel",
  "address": "Bergstraße 123, 82467 Garmisch"
}
```

### Update Property
```
PUT /api/properties/{id}
```

### Delete Property
```
DELETE /api/properties/{id}
```

---

## Scenes Endpoints

### List Scenes
```
GET /api/scenes
```
**Headers:** `Authorization: Bearer <token>`

### Create Scene
```
POST /api/scenes
```
**Body:**
```json
{
  "property_id": "property_uuid",
  "title": "Welcome",
  "content": "Welcome to our hotel!",
  "order": 0
}
```

### Update Scene
```
PUT /api/scenes/{id}
```

### Delete Scene
```
DELETE /api/scenes/{id}
```

---

## Bookings Endpoints

### List Bookings
```
GET /api/bookings
```
**Headers:** `Authorization: Bearer <token>`

### Create Booking
```
POST /api/bookings
```
**Body:**
```json
{
  "property_id": "property_uuid",
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "check_in": "2026-03-01",
  "check_out": "2026-03-05",
  "extras": []
}
```

### Get Booking Invoice
```
GET /api/bookings/{id}/invoice
```
**Returns:** PDF base64 encoded

### Download Invoice
```
GET /api/bookings/{id}/invoice/download
```
**Returns:** PDF file download

---

## Payment Endpoints

### PayPal Create Order
```
POST /api/paypal/create-order
```
**Body:**
```json
{
  "booking_id": "booking_uuid",
  "amount": 100.00
}
```

### PayPal Capture Order
```
POST /api/paypal/capture-order
```
**Body:**
```json
{
  "order_id": "paypal_order_id"
}
```

### Apple Pay Create Order
```
POST /api/apple-pay/create-order
```

### Apple Pay Capture Payment
```
POST /api/apple-pay/capture-payment
```

---

## Analytics Endpoints

### Global Statistics
```
GET /api/stats/global
```

### Host Statistics
```
GET /api/stats/host/{host_id}
```

### Property Statistics
```
GET /api/stats/property/{property_id}
```

### Filtered Booking Statistics
```
POST /api/stats/booking/filter
```
**Body:**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "status": "confirmed",
  "property_id": "property_uuid"
}
```

---

## Export Endpoints

### Export Bookings CSV
```
GET /api/export/bookings/csv
```
**Headers:** `Authorization: Bearer <token>`
**Returns:** CSV file download

### Export Bookings PDF
```
GET /api/export/bookings/pdf
```
**Headers:** `Authorization: Bearer <token>`
**Returns:** PDF file download

### Export Properties CSV
```
GET /api/export/properties/csv
```
**Headers:** `Authorization: Bearer <token>`
**Returns:** CSV file download

---

## Guestview Endpoints

### Get Guestview by Token
```
GET /api/guestview/{token}
```

### Generate Guestview Token
```
POST /api/guestview-token
```
**Body:**
```json
{
  "property_id": "property_uuid"
}
```

---

## Admin Endpoints

### List All Users
```
GET /admin/users
```
**Headers:** `Authorization: Bearer <admin_token>`

### Live Feed
```
GET /admin/bookings/feed
```
**Headers:** `Authorization: Bearer <admin_token>`

---

## Auto-Focus Endpoints

### Get Auto-Focus Config
```
GET /api/autofocus/config
```
**Headers:** `Authorization: Bearer <token>`

### Update Auto-Focus Config
```
PUT /api/autofocus/config
```
**Body:**
```json
{
  "enabled": true,
  "focus_duration_ms": 3000
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error