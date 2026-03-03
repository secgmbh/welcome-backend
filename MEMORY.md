# MEMORY.md - Langzeit-Erinnerungen

## Projekt: Welcome-Link MVP (Stand: 03.03.2026)

### 🔧 AKTUELLER STATUS

**⚠️ RENDER DEPLOY ERFORDERLICH**
- Syntax-Fehler in `backend/server.py` behoben (Invoice PDF unvollständig)
- Commit: `e4d856c` - Code ready, wartet auf Deployment
- **Aktion:** Manuell auf https://dashboard.render.com deployen

### Backend
- API Base URL: `https://api.welcome-link.de`
- Demo Login: `demo@welcome-link.de` / `Demo123!`
- GitHub: `github.com/secgmbh/welcome-backend`
- Hosting: **Render** (nicht GitHub Actions!)

### Frontend
- URL: `https://www.welcome-link.de`
- GitHub: `github.com/secgmbh/welcome-frontend`
- Hosting: **Vercel**
- Gästeseite: `/guestview/QEJHEXP1QF`

### Phase 26-28: Gästeseite Premium (03.03.2026)
- ✅ WLAN Card (Copy, Eye-Toggle)
- ✅ KeySafe Card (Location, versteckter Code)
- ✅ Google Maps Integration (geo: URI)
- ✅ Extras Tab mit Warenkorb
- ✅ Checkout Modal (Stripe/PayPal/Bar)
- ✅ i18n DE/EN Übersetzungen
- ✅ Loading Skeletons
- ✅ Error Handling + Retry
- ✅ QR-Code Scan Tracking
- ⏳ Wartet auf Render Deployment

### Neue Backend Endpoints
- `GET /api/properties/{id}/extras` - Extras einer Property
- `POST /api/checkout` - Checkout erstellen
- `GET /api/checkout/{id}/invoice` - PDF Rechnung
- `POST /api/payment/stripe/create-session` - Stripe Checkout
- `POST /api/payment/paypal/create-order` - PayPal Order
- `POST /api/debug/seed-extras/{id}` - Demo-Extras erstellen
- `POST /api/debug/migrate-qr-scans` - QR-Scans Tabelle

### Wichtige Dateien
- `memory/2026-03-03.md` - Tageslog
- `memory/render-deployment-fix.md` - Deployment Fix Doku
- `memory/improvements-list-04-00.md` - Verbesserungsliste
- `HEARTBEAT.md` - Aktuelle Tasks

### Demo Daten
- Property ID: 17
- public_id: QEJHEXP1QF
- WLAN: Seeblick-Guest / Sommer2024!
- KeySafe: 4287
