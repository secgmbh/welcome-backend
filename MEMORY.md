# MEMORY.md - Langzeit-Erinnerungen

## Projekt: Welcome-Link MVP (Stand: 06.03.2026 - 23:35)

### 🎉 PRODUCTION READY!

**Live URLs:**
- **API:** https://api.welcome-link.de (v2.6.1)
- **Frontend:** https://www.welcome-link.de
- **Dashboard:** https://www.welcome-link.de/dashboard
- **Guestview:** https://www.welcome-link.de/guestview/QEJHEXP1QF
- **Password Reset:** https://www.welcome-link.de/reset-password

**Demo Login:**
- Email: `demo@welcome-link.de`
- Password: `Demo123!`

---

## ✅ Phasen 1-33 COMPLETE

| Phase | Description | Status |
|-------|-------------|--------|
| 1-27 | Core Features | ✅ |
| 28 | Security Headers & Rate Limiting | ✅ |
| 29 | Testing (Backend 42✅, Frontend 30✅) | ✅ |
| 30 | Documentation & Health Check | ✅ |
| 31 | Demo Data & Endpoints | ✅ |
| 32 | Bug Fixes & Optimierung | ✅ |
| 33 | Email Integration + Password Reset | ✅ |

---

## Heutige Errungenschaften (06.03.2026)

### Backend (v2.6.1)
```
Neue Features:
- send_email() - SMTP E-Mail-Versand
- send_magic_link_email() - Magic Link E-Mails mit HTML Template
- send_welcome_email() - Willkommens-E-Mails
- POST /api/auth/password-reset/request - Passwort-Reset anfordern
- POST /api/auth/password-reset/confirm - Passwort zurücksetzen

Email Templates:
- Magic Link Email (HTML + Text)
- Welcome Email (HTML)
- Password Reset Email (HTML)
```

### Frontend
```
Neue Seiten:
- /reset-password - Passwort vergessen Seite
- /auth/reset-password?token=xxx - Neues Passwort setzen

Neue Komponenten:
- ResetPasswordPage.jsx
- ConfirmResetPasswordPage.jsx

Updates:
- LoginPage.jsx - "Passwort vergessen?" Link hinzugefügt
- App.js - Neue Routen für Password Reset
```

### Bug Fixes
```
- ToastProvider import korrigiert (Toast → toast)
- React navigate() Warning - useEffect Fix
- Guestview Endpoint (/api/guestview/{token})
- Unused Imports in BookingCalendar
- Test Suite - 30 tests passing
```

---

## API Endpoints (55 Total)

### Auth Endpoints
```
POST /api/auth/register - Benutzer registrieren
POST /api/auth/login - Benutzer anmelden
GET  /api/auth/me - Aktuellen Benutzer abrufen
POST /api/auth/magic-link - Magic Link anfordern
POST /api/auth/password-reset/request - Passwort-Reset anfordern
POST /api/auth/password-reset/confirm - Passwort zurücksetzen
```

### Property Endpoints
```
GET  /api/properties - Alle Properties
POST /api/properties - Property erstellen
GET  /api/properties/{id} - Property abrufen
PUT  /api/properties/{id} - Property aktualisieren
DELETE /api/properties/{id} - Property löschen
```

### Guestview Endpoints
```
GET  /api/guestview/{token} - Guestview-Daten abrufen
POST /api/guestview-token - Neuen Token generieren
```

### Booking Endpoints
```
GET  /api/bookings - Alle Buchungen
POST /api/bookings - Buchung erstellen
GET  /api/bookings/{id} - Buchung abrufen
```

### Scene Endpoints
```
GET  /api/scenes - Alle Szenen
POST /api/scenes - Szene erstellen
```

### Stats Endpoints
```
GET  /api/stats/global - Globale Statistiken
POST /api/stats/booking/filter - Gefilterte Buchungsstatistiken
```

---

## Tech Stack

### Backend (FastAPI)
- Python 3.11
- FastAPI mit Starlette
- SQLAlchemy ORM
- SQLite Database (192KB)
- JWT Authentication
- Rate Limiting (slowapi)
- Security Headers Middleware

### Frontend (React)
- React 18 mit Vite/CRA
- Tailwind CSS
- React Router v6
- React Query (TanStack Query)
- Lucide Icons
- Dark Mode Support

### Deployment
- Render.com (Backend + Frontend)
- Auto-Deploy on git push
- GitHub Integration

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
```

---

## Demo Data

- **Property:** Ferienwohnung Seeblick (Prien am Chiemsee)
- **Bookings:** 3 (confirmed, pending, completed)
- **Scenes:** 4 (Willkommen, WLAN, Check-out, Umgebung)
- **Extras:** 10 (Frühstück, Sauna, Massage, etc.)
- **Stats:** €5,280 Revenue, 42 Bookings

---

## Git Commits (06.03.2026)

```
Backend:
- feat: Add SMTP email integration with magic link support (v2.6.0)
- feat: Add password reset functionality (v2.6.1)

Frontend:
- fix: Remove unused imports in BookingCalendar component
- fix: Guestview endpoint - use /api/guestview/{token}
- feat: Add password reset pages
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

## Nächste Schritte (TODO für morgen)

1. **Email Templates verfeinern**
   - Booking Confirmation Email
   - Payment Receipt Email
   - Guest Welcome Email

2. **Frontend Password Reset testen**
   - E2E Test auf Production
   - Email Delivery Check

3. **Production Monitoring**
   - Sentry Dashboard einrichten
   - Error Alerts konfigurieren

4. **Performance Optimierung**
   - Bundle Size reduzieren
   - Lazy Loading verbessern

5. **CI/CD Pipeline**
   - GitHub Actions einrichten
   - Automated Tests

---

## Wichtige Dateien

- `TODO_GUESTVIEW.md` - Feature-Status
- `HEARTBEAT.md` - Aktuelle Aufgaben
- `memory/YYYY-MM-DD.md` - Tägliche Logs
- `backend/USER_GUIDE.md` - User Dokumentation
- `backend/server.py` - Haupt-API-Datei (2000+ Zeilen)

---

## Kontakte & URLs

- **GitHub:** secgmbh/welcome-backend, secgmbh/welcome-frontend
- **Render:** welcome-link-backend, welcome-frontend
- **Support:** support@welcome-link.de