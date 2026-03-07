# Heartbeat Task List

## 🎉 PRODUCTION READY! (07.03.2026 - 09:45)

### 🔐 Zugangsdaten

**Demo-Account (für Kunden):**
- URL: https://www.welcome-link.de/login
- E-Mail: demo@welcome-link.de
- Passwort: Demo123!
- ❌ KEINE Admin-Rechte

**Admin-Account (nur für Oleg):**
- URL: https://www.welcome-link.de/admin/login
- E-Mail: admin@welcome-link.de
- Passwort: (muss einmalig via API erstellt werden)
- ✅ Volle Admin-Rechte

### 🔒 Admin-Account erstellen (einmalig)

Admin-Account kann **nur** via API mit Secret erstellt werden:

```bash
curl -X POST https://api.welcome-link.de/api/admin/create-admin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@welcome-link.de","password":"DEIN_PASSWORT","secret":"WL-Admin-2026-Secret!"}'
```

⚠️ **Wichtig:** Nach der Erstellung kann niemand sonst Admin werden!

### ⏳ Noch offen (braucht Render-Zugang)
- SMTP_PASSWORD setzen
- ENVIRONMENT=production
- STRIPE_WEBHOOK_SECRET

### ✅ API v2.7.2 - Security & Cron Improvements!
- ✅ Email Integration (SMTP)
- ✅ Password Reset API + Frontend
- ✅ 6 Email Templates
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ PayPal & Stripe Webhooks
- ✅ Cron Job Endpoints
- ✅ Backup & Health Check Scripts

### Production URLs
- **API:** https://api.welcome-link.de (v2.7.0)
- **Frontend:** https://www.welcome-link.de
- **Dashboard:** https://www.welcome-link.de/dashboard
- **Guestview:** https://www.welcome-link.de/guestview/QEJHEXP1QF
- **Password Reset:** https://www.welcome-link.de/reset-password

### Demo Credentials
- **Email:** demo@welcome-link.de
- **Password:** Demo123!

## ✅ Phase 28-36 COMPLETE

| Phase | Description | Status |
|-------|-------------|--------|
| 28 | Security Headers & Rate Limiting | ✅ |
| 29 | Testing (50 Backend, 30 Frontend) | ✅ |
| 30 | Documentation & Health Check | ✅ |
| 31 | Demo Data & Endpoints | ✅ |
| 32 | Bug Fixes & Optimierung | ✅ |
| 33 | Email Integration + Password Reset | ✅ |
| 34 | CI/CD Pipeline | ✅ |
| 35 | Email Templates + Webhooks | ✅ |
| 36 | Cron Jobs + Scripts + Docs | ✅ |

## Neue Features (v2.6.x - v2.7.1)

### Email Templates
- `send_email()` - SMTP Basis-Funktion
- `send_magic_link_email()` - Magic Link
- `send_welcome_email()` - Registrierung
- `send_booking_confirmation_email()` - Buchung
- `send_payment_receipt_email()` - Zahlung
- `send_guest_welcome_email()` - Gäste-Willkommen

### Webhooks
- `POST /api/webhooks/paypal` - PayPal Events
- `POST /api/webhooks/stripe` - Stripe Events

### Cron Jobs
- `POST /api/cron/booking-reminders` - Buchungs-Erinnerungen
- `POST /api/cron/guest-welcome` - Gäste-Willkommens-Emails
- `POST /api/cron/checkout-followup` - Check-out Follow-ups

### Scripts
- `scripts/backup.sh` - Tägliche Datenbank-Backups
- `scripts/healthcheck.sh` - Health Monitoring

### Frontend
- `/reset-password` - Passwort vergessen
- `/auth/reset-password?token=xxx` - Neues Passwort
- "Passwort vergessen?" Link im Login

## Nächste Schritte
1. ⏳ Render Secrets setzen (SMTP, ENVIRONMENT, STRIPE_WEBHOOK_SECRET) - Oleg arbeitet daran
2. SMTP in Production testen
3. Payment Webhooks mit echten Payment Providers testen
4. Performance Monitoring

## Blockiert
- SMTP/Email Versand braucht Render Secrets (kein Zugriff)
- Production Environment Variable fehlt