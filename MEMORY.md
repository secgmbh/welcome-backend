# MEMORY.md - Langzeit-Erinnerungen

## Projekt: Welcome-Link MVP (Stand: 16.03.2026 - 04:35)

### ✅ NEU: User Management & Subscription (16.03.2026)

**Neue Felder in User-Tabelle:**
- `phone` - Telefonnummer
- `company_name` - Firmenname
- `plan` - Subscription Plan (free/starter/pro/enterprise)
- `trial_ends_at` - Trial-Ende
- `max_properties` - Max Properties je Plan
- `stripe_customer_id` - Stripe Customer ID
- `is_active` - Account Status

**Neue API Endpoints:**
- `PUT /api/auth/profile` - Profil aktualisieren

---

## 🎉 PRODUCTION READY!

**Live URLs:**
- **API:** https://api.welcome-link.de (v2.7.3)
- **Frontend:** https://www.welcome-link.de
- **Dashboard:** https://www.welcome-link.de/dashboard
- **Guestview:** https://www.welcome-link.de/guestview/QEJHEXP1QF
- **Password Reset:** https://www.welcome-link.de/reset-password

**Demo Login:**
- Email: `demo@welcome-link.de`
- Password: `Demo123!`

---

## ✅ Phasen 1-36 COMPLETE

| Phase | Description | Status |
|-------|-------------|--------|
| 1-27 | Core Features | ✅ |
| 28 | Security Headers & Rate Limiting | ✅ |
| 29 | Testing (50 Backend, 30 Frontend) | ✅ |
| 30 | Documentation & Health Check | ✅ |
| 31 | Demo Data & Endpoints | ✅ |
| 32 | Bug Fixes & Optimierung | ✅ |
| 33 | Email Integration + Password Reset | ✅ |
| 34 | CI/CD Pipeline | ✅ |
| 35 | Email Templates + Webhooks | ✅ |
| 36 | Cron Job Endpoints | ✅ |

---

## API Endpoints (60+)

### Auth (7)
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/magic-link
POST /api/auth/password-reset/request
POST /api/auth/password-reset/confirm
POST /api/auth/demo/init
```

### Properties (6)
```
GET  /api/properties
POST /api/properties
GET  /api/properties/{id}
PUT  /api/properties/{id}
DELETE /api/properties/{id}
GET  /api/properties/{id}/extras
```

### Bookings (4)
```
GET  /api/bookings
POST /api/bookings
GET  /api/bookings/{id}
GET  /api/bookings/feed
```

### Guestview (2)
```
GET  /api/guestview/{token}
POST /api/guestview-token
```

### Webhooks (2)
```
POST /api/webhooks/paypal
POST /api/webhooks/stripe
```

### Cron Jobs (3)
```
POST /api/cron/booking-reminders
POST /api/cron/guest-welcome
POST /api/cron/checkout-followup
```

---

## Email Templates (6)

| Template | Funktion | Trigger |
|----------|----------|---------|
| `send_magic_link_email()` | Magic Link Login | Auth Request |
| `send_welcome_email()` | Registrierung | Nach Registrierung |
| `send_password_reset_email()` | Passwort Reset | Request |
| `send_booking_confirmation_email()` | Buchungsbestätigung | create_booking() |
| `send_payment_receipt_email()` | Zahlungsbestätigung | Webhook |
| `send_guest_welcome_email()` | Gäste-Willkommen | Cron Job |

---

## Git Commits (06./07.03.2026)

### Backend Commits
```
v2.6.0: feat: Add SMTP email integration
v2.6.1: feat: Add password reset functionality
v2.6.2: feat: Add booking confirmation email template
v2.6.3: feat: Add payment receipt email template
v2.6.4: feat: Add guest welcome email template
v2.6.5: feat: Integrate booking confirmation email in create_booking
v2.7.0: feat: Add PayPal and Stripe webhook handlers
v2.7.1: feat: Add cron job endpoints for booking reminders
test: Add password reset validation tests
test: Add E2E tests for API endpoints
test: Fix E2E tests - all 50 tests passing
ci: Add GitHub Actions CI/CD pipeline
```

### Frontend Commits
```
fix: Remove unused imports in BookingCalendar
fix: Guestview endpoint - use /api/guestview/{token}
fix: Ensure password reset link shows in login
feat: Add password reset pages
feat: Update LoginPage with "Passwort vergessen?" link
```

---

## Test Status

### Backend Tests (50 passing)
```
tests/test_api.py - API endpoints
tests/test_security.py - Security headers
tests/test_password_reset.py - Password reset validation
tests/test_e2e.py - E2E flow tests
tests/test_load.py - Load tests
```

### Frontend Tests (30 passing)
```
Login/Register tests
Dashboard tests
Component tests
```

---

## Backend Commits (12.03.2026)

### v2.7.3 - Performance Monitoring (12.03.2026)
```
feat: Add performance monitoring middleware and enhanced health check
- RequestTimingMiddleware für Request Processing Time
- Enhanced /health endpoint mit System Metrics
- X-Process-Time-Ms Header für alle Responses
- Slow Request Logging (>500ms)
- Database Health Check mit SQLite Connection Test
```

### Frontend E2E Tests (12.03.2026)
```
test: Add comprehensive E2E test suite
- auth.spec.ts: Login, Demo Login
- dashboard.spec.ts: Navigation, Tabs
- homepage.spec.ts: Navigation, CTAs
- admin.spec.ts: Admin Login, Panel
- guestview.spec.ts: Guest View
- performance.spec.ts: Load Time, Core Web Vitals
- pricing.spec.ts: Pricing Page
- features.spec.ts: Features, Integrations
- checkout.spec.ts: Checkout Flow, Guestview
- register.spec.ts: Registration, Password Reset
- error-pages.spec.ts: 404, Accessibility
```

---

## Test Status (12.03.2026)

### Frontend Bundle
- Main Bundle: ~425KB
- Total Build: ~9.1MB
- Static JS: ~8.8MB

### E2E Tests
- Total Test Files: 11
- Coverage: Auth, Dashboard, Admin, Guestview, Performance, Checkout, Register, Error Pages
```
feat: Add performance monitoring middleware and enhanced health check
- RequestTimingMiddleware für Request Processing Time
- Enhanced /health endpoint mit System Metrics
- X-Process-Time-Ms Header für alle Responses
- Slow Request Logging (>500ms)
- Database Health Check mit SQLite Connection Test
```

### v2.7.2 - Security & Cron Improvements (07.03.2026)
```
feat: Improve Stripe webhook security and activate real booking queries
- Stripe webhook signature verification (security)
- Real booking queries for cron jobs activated
- STRIPE_WEBHOOK_SECRET environment variable added
```

## Test-Ergebnisse (07.03.2026)

### ✅ Funktional
| Test | Status |
|------|--------|
| Login API | ✅ |
| Password Reset Request | ✅ |
| Cron: Booking Reminders | ✅ |
| Cron: Guest Welcome | ✅ |
| Cron: Checkout Followup | ✅ |
| PayPal Webhook | ✅ |
| Stripe Webhook | ✅ |

### ❌ Benötigt Render-Zugang
| Issue | Status |
|-------|--------|
| SMTP_PASSWORD nicht gesetzt | ❌ Braucht Render Secrets |
| ENVIRONMENT = development | ❌ Sollte production sein |
| STRIPE_WEBHOOK_SECRET | ❌ Neu hinzugefügt |

---

## Security Status ✅

```
Content-Security-Policy: ✅
X-Content-Type-Options: nosniff ✅
X-Frame-Options: DENY ✅
X-XSS-Protection: 1; mode=block ✅
Rate Limiting: ✅ (Auth Endpoints)
JWT Auth: ✅
SMTP: ✅ (Configured)
Sentry: ✅ (Ready)
CI/CD: ✅ (GitHub Actions)
Webhooks: ✅ (PayPal, Stripe)
```

---

## Performance

```
API Response Times:
/api/auth/login: 79ms
/api/properties: 60ms
/api/guestview: 103ms
/api/bookings: 60ms
/api/stats/global: 45ms

Frontend Bundle: ~450KB
```

---

## Environment Variables

### Backend (.env)
```
SECRET_KEY=xxx (min 32 Zeichen)
DATABASE_URL=sqlite:///./app.db
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=xxx
SMTP_PASSWORD=xxx
SMTP_FROM=noreply@welcome-link.de
SENTRY_DSN=xxx (optional)
```

---

## Kontakte

- **GitHub:** secgmbh/welcome-backend, secgmbh/welcome-frontend
- **Render:** welcome-link-backend, welcome-frontend
- **Support:** support@welcome-link.de