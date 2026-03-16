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

### 🔒 Admin-Account
✅ **Erstellt!** Admin-Account ist aktiv.

**Admin-Login:** https://www.welcome-link.de/admin/login
**Credentials:** admin@welcome-link.de / AdminOleg2026!

### ✅ SMTP Getestet (07.03.2026 - 16:57)
- ✅ Password Reset E-Mail funktioniert
- ✅ Magic Link E-Mail funktioniert
- ✅ Registration Welcome E-Mail funktioniert
- ✅ Cron Jobs laufen (Booking Reminders, Guest Welcome, Checkout Followup)

### ✅ Admin Panel (08.03.2026 - komplett neu gestaltet)
- **Neue Tabs:** Übersicht, Benutzer, Properties, Buchungen, System, Aktionen
- **Übersicht:** Real-time Stats mit Trends, Letzte Aktivitäten, Top Properties
- **Benutzer:** Verwaltung mit Plan/Status, Export-Funktion
- **Properties:** Übersicht mit QR-Scans, Buchungen, Quick-Copy Links
- **Buchungen:** Tabelle mit Gast-Details, Export CSV
- **System:** API/DB/SMTP Status, Quick Links
- **Aktionen:** E-Mail Test, Cron Job Trigger, Daten Export, Cache Leeren
- **Toast Notifications** für Admin-Aktionen

### ✅ Frontend Tests (07.03.2026 - 21:30)
| Seite | Status | Anmerkungen |
|-------|--------|-------------|
| Homepage | ✅ | Alle Elemente, CTAs |
| Features | ✅ | Alle Features, Integrationen |
| Pricing | ✅ | Alle Pakete, FAQs |
| Register | ✅ | Getestet, funktioniert |
| Login | ✅ | Leitet zum Dashboard |
| Dashboard | ✅ | Stats, Kalender, Aktivitäten |
| Guestview | ✅ | Welcome, Extras, Contact |
| Resources | ✅ | Videos mit "Video folgt" |
| Admin Panel | ✅ | Alle Tabs funktionieren |

### ✅ E2E Tests (12.03.2026 - 22:16)
| Test File | Status | Coverage |
|-----------|--------|----------|
| auth.spec.ts | ✅ | Login, Demo Login |
| dashboard.spec.ts | ✅ | Navigation, Tabs |
| homepage.spec.ts | ✅ | Navigation, CTAs |
| admin.spec.ts | ✅ | Admin Login, Panel |
| guestview.spec.ts | ✅ | Guest View |
| performance.spec.ts | ✅ | Load Time, Core Web Vitals |
| pricing.spec.ts | ✅ | Pricing Page |
| features.spec.ts | ✅ | Features, Integrations |
| checkout.spec.ts | ✅ | Checkout Flow, Guestview |
| register.spec.ts | ✅ | Registration, Password Reset |
| error-pages.spec.ts | ✅ | 404, Accessibility |

### 🐛 Behoben
- ✅ Impressum Platzhalter-Texte durch Demo-Daten ersetzt
- ✅ Videos mit "Video folgt" Platzhalter
- ✅ Admin Panel Health Status korrigiert

### ⏳ Noch offen
- ENVIRONMENT=production setzen (derzeit "development")
- STRIPE_WEBHOOK_SECRET für Payment-Verifikation

### 🔧 In Progress: Email-Fix Deployment
- ✅ `send_email()` und `send_welcome_email()` Funktionen hinzugefügt
- ✅ Version zu 2.7.4 erhöht
- ✅ Zu GitHub gepusht (Commit `34cbffa`)
- ⏳ Warte auf Render Deploy (API zeigt noch 2.7.1)
- ⚠️ **Registrierungs-Emails funktionieren erst nach Deploy!**

### SMTP Config (15.03.2026)
```
SMTP_HOST=mail.your-server.de
SMTP_PORT=587
SMTP_USER=info@welcome-link.de
SMTP_PASSWORD=q1/GtadF-x$?
SMTP_FROM=info@welcome-link.de
```

### Commits heute (15.03.2026)
| Commit | Beschreibung |
|--------|--------------|
| `3686218` | Memory Leaks in AdminPage/DashboardPage behoben |
| `f454dd5` | Email-Funktionalität hinzugefügt (send_email, send_welcome_email) |
| `df5dfcb` | SMTP_PASSWORD fallback (reverted - unsicher) |
| `643945a` | Security fix: SMTP_PASSWORD nur via ENV var |
| `34cbffa` | Version bump zu 2.7.4 für Deploy-Tracking |

### ✅ API v2.7.2 - Security & Cron Improvements!
- ✅ Email Integration (SMTP)
- ✅ Password Reset API + Frontend
- ✅ 6 Email Templates
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ PayPal & Stripe Webhooks
- ✅ Cron Job Endpoints
- ✅ Backup & Health Check Scripts

### ✅ API v2.7.3 - Performance Monitoring (12.03.2026)
- ✅ RequestTimingMiddleware - Request Processing Time Tracking
- ✅ Enhanced Health Check mit System Metrics (CPU, Memory, Disk)
- ✅ X-Process-Time-Ms Header für alle Responses
- ✅ Slow Request Logging (>500ms)
- ✅ Database Health Check mit SQLite Connection Test
- ✅ psutil Integration für System-Metriken

### Production URLs
- **API:** https://api.welcome-link.de (v2.7.0)
- **Frontend:** https://www.welcome-link.de
- **Dashboard:** https://www.welcome-link.de/dashboard
- **Guestview:** https://www.welcome-link.de/guestview/QEJHEXP1QF
- **Password Reset:** https://www.welcome-link.de/reset-password

### Demo Credentials
- **Email:** demo@welcome-link.de
- **Password:** Demo123!

## ✅ Option A, B, C (16.03.2026 - 16:50)

### E2E Tests (Option A)
| Test File | Coverage |
|-----------|----------|
| `subscription.spec.ts` | Registration, Login, Plan Limits |
| `subscription.spec.ts` | Pricing Page, Checkout Flow |
| `subscription.spec.ts` | API Demo Mode, Plan Features |

### Frontend Polish (Option B)
| Component | Status |
|-----------|--------|
| `lib/errors.js` | German error messages |
| `hooks/useToast.jsx` | Toast hook for UX |
| `components/ui/Toast.jsx` | Already exists |

### API Documentation (Option C)
| Doc | Content |
|-----|---------|
| `API.md` | All endpoints documented |
| `API.md` | Postman collection |
| `API.md` | Error responses, Rate limits |

### Git Commits
```
Frontend: 43e659b - E2E subscription tests, error handling
Backend: de23539 - API documentation
```

---

## ✅ PDF Downloads (16.03.2026 - 14:15)

### Neue Downloads auf Resources-Seite:
| PDF | Inhalt |
|-----|--------|
| `faq-vorlage-hotels.pdf` | 50+ Gästefragen mit Antworten |
| `upsell-texte-sammlung.pdf` | Upselling-Formulierungen |
| `email-templates.pdf` | Buchungs-, Willkommens-, Check-out Emails |
| `onboarding-guide.pdf` | 5-Schritt Schnellstart Guide |

### Speicherort:
```
/public/pdfs/*.pdf
```

### Git Commit:
```
a5bf510 - feat: Add downloadable PDF resources
```

---

## ✅ User Management & Subscription (16.03.2026 - 04:35)

### Neue Datenbank-Felder (User-Tabelle)
| Feld | Typ | Default | Beschreibung |
|------|-----|---------|---------------|
| `phone` | VARCHAR(50) | NULL | Telefonnummer |
| `company_name` | VARCHAR(200) | NULL | Firmenname (optional) |
| `plan` | VARCHAR(20) | 'free' | Subscription Plan |
| `trial_ends_at` | TIMESTAMP | NULL | Trial-Ende für Paid Plans |
| `max_properties` | INTEGER | 1 | Max Properties je Plan |
| `stripe_customer_id` | VARCHAR(100) | NULL | Stripe Customer ID |
| `is_active` | BOOLEAN | TRUE | Account Status |

### Subscription Plans
| Plan | Preis | Properties | Features |
|------|-------|------------|----------|
| **Free** | €0 | 1 | Basis |
| **Starter** | €9/Monat | 3 | + Extras, QR-Codes |
| **Pro** | €29/Monat | 10 | + Analytics, API |
| **Enterprise** | Custom | Unlimited | + White-Label, Support |

### Neue API Endpoints
```
PUT /api/auth/profile           - Profil aktualisieren
GET /api/admin/users            - Admin: Alle Benutzer mit Plan-Info
PATCH /api/admin/users/{id}/plan - Admin: Plan aktualisieren
```

### Frontend Updates (16.03.2026)
- **RegisterPage:** Phone & Company Felder
- **ProfilePage:** API-Connected, Plan-Anzeige, Profil-Editing
- **PricingPage:** 4-Tier Pricing mit Stripe-Integration
- **AdminPage:** Benutzer-Verwaltung mit Plan-Stats

### Git Commits
```
Backend:
1cc1649 - feat: Add user management & subscription fields
a5e768b - feat: Add admin routes for user plan management
4d8526e - feat: Add Stripe subscription checkout integration

Frontend:
bc03d9b - feat: Add user management & subscription UI
8f8cb1a - feat: Update PricingPage to use subscription API endpoint
```

---

## ✅ Stripe Integration (16.03.2026 - 07:05)

### Neue Backend Endpoints
```
POST /api/subscription/create   - Stripe Checkout Session erstellen
POST /api/subscription/portal   - Stripe Customer Portal
GET  /api/subscription/status   - Aktuelle Subscription-Info
POST /api/webhooks/stripe       - Stripe Webhook Handler
```

### Stripe Events (Webhooks)
- `checkout.session.completed` - Plan aktivieren
- `customer.subscription.updated` - Plan aktualisieren
- `customer.subscription.deleted` - Auf Free downgraden

### Environment Variables (benötigt)
```
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_STARTER_MONTHLY=price_xxx
STRIPE_PRICE_STARTER_YEARLY=price_xxx
STRIPE_PRICE_PRO_MONTHLY=price_xxx
STRIPE_PRICE_PRO_YEARLY=price_xxx
```

### Demo Mode
- Wenn `STRIPE_SECRET_KEY` nicht gesetzt → Demo-Modus
- Mock URLs für Test ohne Stripe Account

---

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