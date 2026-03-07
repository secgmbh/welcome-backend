# Welcome Link - API Dokumentation

## Übersicht

Die Welcome Link API ermöglicht die Verwaltung von Ferienunterkünften, Buchungen und Gästen.

**Base URL:** `https://api.welcome-link.de`

**Version:** 2.7.1

---

## Authentifizierung

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
    "id": 1,
    "email": "demo@welcome-link.de",
    "name": "Demo User",
    "is_demo": true
  }
}
```

### Authenticated Requests
```http
GET /api/auth/me
Authorization: Bearer <token>
```

---

## Endpoints

### Authentifizierung

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| POST | `/api/auth/register` | Neuen Benutzer registrieren |
| POST | `/api/auth/login` | Benutzer anmelden |
| GET | `/api/auth/me` | Aktuellen Benutzer abrufen |
| POST | `/api/auth/magic-link` | Magic Link anfordern |
| POST | `/api/auth/password-reset/request` | Passwort-Reset anfordern |
| POST | `/api/auth/password-reset/confirm` | Passwort zurücksetzen |

### Properties

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/properties` | Alle Properties abrufen |
| POST | `/api/properties` | Property erstellen |
| GET | `/api/properties/{id}` | Property abrufen |
| PUT | `/api/properties/{id}` | Property aktualisieren |
| DELETE | `/api/properties/{id}` | Property löschen |
| GET | `/api/properties/{id}/extras` | Extras abrufen |
| GET | `/api/properties/{id}/scenes` | Szenen abrufen |

### Bookings

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/bookings` | Alle Buchungen abrufen |
| POST | `/api/bookings` | Buchung erstellen |
| GET | `/api/bookings/{id}` | Buchung abrufen |
| GET | `/api/bookings/feed` | Buchungs-Feed abrufen |

### Guestview

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/guestview/{token}` | Guestview-Daten abrufen |
| POST | `/api/guestview-token` | Neuen Token generieren |

### Stats

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/stats/global` | Globale Statistiken |
| POST | `/api/stats/booking/filter` | Gefilterte Statistiken |

### Export

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/export/bookings/csv` | Buchungen als CSV exportieren |
| GET | `/api/export/bookings/pdf` | Buchungen als PDF exportieren |

### Webhooks

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| POST | `/api/webhooks/paypal` | PayPal Webhook |
| POST | `/api/webhooks/stripe` | Stripe Webhook |

### Cron Jobs

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| POST | `/api/cron/booking-reminders` | Buchungs-Erinnerungen senden |
| POST | `/api/cron/guest-welcome` | Gäste-Willkommens-Emails senden |
| POST | `/api/cron/checkout-followup` | Check-out Follow-ups senden |

---

## Rate Limiting

Die folgenden Endpoints haben Rate Limiting:

| Endpoint | Limit |
|----------|-------|
| `/api/auth/register` | 5 requests/minute |
| `/api/auth/login` | 10 requests/minute |
| `/api/auth/magic-link` | 3 requests/minute |
| `/api/auth/password-reset/request` | 3 requests/minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1614556800
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Not Found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many requests"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Email Templates

Die API sendet automatisch E-Mails bei folgenden Events:

| Event | Template |
|-------|----------|
| Registrierung | Welcome Email |
| Magic Link | Magic Link Email |
| Passwort Reset | Password Reset Email |
| Buchung erstellt | Booking Confirmation Email |
| Zahlung erhalten | Payment Receipt Email |
| Check-in | Guest Welcome Email |

---

## Webhooks

### PayPal Webhook
```json
{
  "event_type": "PAYMENT.CAPTURE.COMPLETED",
  "resource": {
    "id": "ABC123",
    "amount": {
      "value": "100.00"
    }
  }
}
```

### Stripe Webhook
```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_ABC123",
      "amount": 10000
    }
  }
}
```

---

## SDK Beispiel

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const API_URL = 'https://api.welcome-link.de';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
async function login(email: string, password: string) {
  const response = await api.post('/api/auth/login', { email, password });
  localStorage.setItem('token', response.data.token);
  return response.data;
}

// Get properties
async function getProperties() {
  const response = await api.get('/api/properties');
  return response.data;
}

// Create booking
async function createBooking(booking: {
  property_id: number;
  guest_name: string;
  guest_email: string;
  check_in: string;
  check_out: string;
}) {
  const response = await api.post('/api/bookings', booking);
  return response.data;
}
```

---

## Changelog

### v2.7.1 (07.03.2026)
- Added cron job endpoints for booking reminders

### v2.7.0 (07.03.2026)
- Added PayPal and Stripe webhook handlers

### v2.6.5 (07.03.2026)
- Integrated booking confirmation email in create_booking

### v2.6.4 (07.03.2026)
- Added guest welcome email template

### v2.6.3 (07.03.2026)
- Added payment receipt email template

### v2.6.2 (07.03.2026)
- Added booking confirmation email template

### v2.6.1 (06.03.2026)
- Added password reset functionality

### v2.6.0 (06.03.2026)
- Added SMTP email integration

### v2.5.3 (06.03.2026)
- Security headers and rate limiting