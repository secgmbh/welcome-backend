# MEMORY.md - Langzeit-Erinnerungen

## Projekt: Welcome-Link MVP (Stand: 06.03.2026)

### 🎉 PRODUCTION READY!

**Live URLs:**
- **API:** https://api.welcome-link.de (v2.5.3)
- **Frontend:** https://www.welcome-link.de
- **Dashboard:** https://www.welcome-link.de/dashboard
- **Guestview:** https://www.welcome-link.de/guestview/QEJHEXP1QF

**Demo Login:**
- Email: `demo@welcome-link.de`
- Password: `Demo123!`

---

## ✅ Phasen 1-32 COMPLETE

| Phase | Description | Status |
|-------|-------------|--------|
| 1-27 | Core Features | ✅ |
| 28 | Security Headers & Rate Limiting | ✅ |
| 29 | Testing (Backend, Frontend, E2E) | ✅ |
| 30 | Documentation & Health Check | ✅ |
| 31 | Demo Data & Endpoints | ✅ |
| 32 | Frontend Build Fix | ✅ |

---

## Demo Data

- **Property:** Ferienwohnung Seeblick (Prien am Chiemsee)
- **Bookings:** 3 (confirmed, pending, completed)
- **Scenes:** 4 (Willkommen, WLAN, Check-out, Umgebung)
- **Extras:** 10 (Frühstück, Sauna, Massage, etc.)
- **Stats:** €5,280 Revenue, 42 Bookings

---

## API Endpoints

```
# Auth
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

# Guestview
GET  /api/guestview/{token}
POST /api/guestview-token

# CRUD
GET/POST /api/properties
GET/POST /api/bookings
GET/POST /api/scenes
GET/POST /api/extras

# Stats
GET  /api/stats/global
POST /api/stats/booking/filter

# Export
GET  /api/export/bookings/csv
GET  /api/export/bookings/pdf

# Payment
POST /api/paypal/create-order
POST /api/paypal/capture-order
POST /api/checkout
```

---

## Bug Fixes (06.03.2026)

1. **ToastProvider Import** - Pfad korrigiert (`Toast` → `toast`)
2. **is_ Spalte** - User Model mit include_properties
3. **Environment Variables** - VITE_API_URL für Frontend

---

## Wichtige Dateien

- `TODO_GUESTVIEW.md` - Feature-Status
- `HEARTBEAT.md` - Aktuelle Aufgaben
- `memory/YYYY-MM-DD.md` - Tägliche Logs
- `backend/USER_GUIDE.md` - User Dokumentation

---

## Git Branches

- **main** - Production (deployed)
- **nightly-improvements** - Development (merged)

---

## Render Deployment

- Backend: `welcome-link-backend` auf Render
- Frontend: `welcome-frontend` auf Render
- Auto-Deploy: Aktiviert (push auf main)

---

## Nächste Schritte (Optional)

1. Production Monitoring (Sentry Dashboard)
2. CI/CD Pipeline Optimization
3. Feature Flags System
4. Performance Monitoring Dashboard