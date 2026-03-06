# TODO Guestview - Welcome Link MVP

## ✅ Abgeschlossene Phasen

### Phase 1: Core Auth + Guestview API ✅ COMPLETE
- [x] Backend API Server (FastAPI)
- [x] SQLite Datenbank
- [x] JWT Auth System
- [x] User Registration/Login
- [x] Guestview API Endpoints

### Phase 2: Host Dashboard ✅ COMPLETE
- [x] Dashboard UI
- [x] Properties CRUD
- [x] QR Code Generator
- [x] Guestview Generator

### Phase 3: Analytics Dashboard ✅ COMPLETE
- [x] Booking Statistiken
- [x] Umsatz-Übersicht
- [x] Guestview Analytics

### Phase 4: Profilverwaltung + Buchungen ✅ COMPLETE
- [x] User Profile API
- [x] Invoice Daten
- [x] Buchungs-Management

### Phase 5: Guest Booking Form ✅ COMPLETE
- [x] Guest Booking UI
- [x] Booking API
- [x] E-Mail Bestätigung

### Phase 6: Info-Szenen API ✅ COMPLETE
- [x] Scenes CRUD API
- [x] Scene Templates

### Phase 7: Frontend Szenen Editor ✅ COMPLETE
- [x] Scene Editor UI
- [x] Drag & Drop

### Phase 8: A/B Testing UI, Extras, Bundles ✅ COMPLETE
- [x] A/B Testing Framework
- [x] Extras Verwaltung
- [x] Bundle Angebote

### Phase 9: Partner API + UI, Smart Rules ✅ COMPLETE
- [x] Partner API
- [x] Smart Rules Backend

### Phase 10: Guest Features ✅ COMPLETE
- [x] Cart System
- [x] Walkthrough
- [x] Feedback
- [x] Tipping

### Phase 11: Booking API ✅ COMPLETE
- [x] Booking CRUD
- [x] Status Management

### Phase 12: Cleaner & Task API ✅ COMPLETE
- [x] Cleaner API
- [x] Task Management

### Phase 13: Global Stats API ✅ COMPLETE
- [x] Global Statistics
- [x] Host Stats

### Phase 14: Branding & AI Enhancement ✅ COMPLETE
- [x] Branding API
- [x] AI Copywriter

### Phase 15-18: Weitere Entwicklungen ✅ COMPLETE

### Phase 19: Quality & Polish ✅ COMPLETE
- [x] A/B Testing UI
- [x] Store-Konfigurator

### Phase 20: Checkout & Rechnungen ✅ COMPLETE
- [x] PayPal Integration
- [x] Apple Pay Integration
- [x] Google Pay Integration
- [x] PDF Rechnung
- [x] E-Mail Rechnungsversand
- [x] Checkout-Seite für Gäste

### Phase 21: Dashboard & Admin Features ✅ COMPLETE
- [x] Nutzerverwaltung Backend API
- [x] Nutzerverwaltung Frontend UI
- [x] Live-Feed Buchungen
- [x] Auto-focus API Fix

### Phase 22: Admin Features ✅ COMPLETE
- [x] Live-Feed UI

### Phase 23: Analytics & Reports ✅ COMPLETE
- [x] Booking Statistiken Dashboard
- [x] Export Funktionen (CSV, PDF)
- [x] Umsatzberichte

### Phase 24: Export & Reports ✅ COMPLETE
- [x] CSV Export
- [x] PDF Berichte

### Phase 25: Dashboard Features ✅ COMPLETE
- [x] Filter API
- [x] Filter UI
- [x] AnalyticsPage in Dashboard
- [x] Export UI im Dashboard

### Phase 26: Finishing & Polish ✅ COMPLETE
- [x] Auto-focus UI Fix
- [x] Export UI im Dashboard
- [x] Documentation
- [x] Error Logging
- [x] Feedback API
- [x] Keyboard Shortcuts
- [x] Branding Engine UI

### Phase 27: Quality Features ✅ COMPLETE
- [x] Branding Engine UI
- [x] Smart Rules UI
- [x] Kalender-Sync (.ics Export)

---

## 🚧 Phase 28: Production Readiness (IN BEARBEITUNG)

- [x] Environment Variables Check ✅ (Hardcoded Secrets entfernt)
- [x] Security Headers ✅ (X-Frame-Options, CSP, HSTS, etc.)
- [x] Rate Limiting ✅ (Auth Endpoints: 5-10 req/min)
- [x] Input Validation ✅ (Pydantic EmailStr, Field validators)
- [x] Error Handling ✅ (Global Exception Handler)
- [x] Logging & Monitoring ✅ (JSON Logging für Production)

---

## 📝 Backend API Übersicht

```
# Auth Endpoints
POST /api/auth/register     # User Registration
POST /api/auth/login        # User Login
GET  /api/auth/me           # Current User
PUT  /api/auth/profile      # Profile Update

# Guestview Endpoints
GET  /api/guestview/{token}  # Passwortlose Ansicht
POST /api/guestview-token    # Guestview Token generieren

# Scenes Endpoints
GET  /api/scenes             # Alle Scenes
POST /api/scenes             # Neue Scene erstellen
PUT  /api/scenes/{id}        # Scene aktualisieren
DELETE /api/scenes/{id}      # Scene löschen

# Bookings Endpoints
GET  /api/bookings           # Buchungen
POST /api/bookings           # Neue Buchung
GET  /api/bookings/{id}/invoice # Rechnung downloaden
GET  /api/bookings/calendar.ics # Kalender Export

# Stats Endpoints
GET  /api/stats/global       # Globale Statistiken
GET  /api/stats/host/{id}    # Host-spezifische Statistiken
GET  /api/stats/property/{id} # Property-spezifische Statistiken
POST /api/stats/booking/filter # Gefilterte Buchungs-Statistiken

# Export Endpoints
GET  /api/export/bookings/csv  # CSV Export
GET  /api/export/bookings/pdf  # PDF Export
GET  /api/export/properties/csv # Properties Export

# Payment Endpoints
POST /api/paypal/create-order  # PayPal Order
POST /api/paypal/capture-order # PayPal Capture
POST /api/apple-pay/create-order # Apple Pay Order

# Feedback Endpoint
POST /api/feedback           # Feedback senden

# Auto-Focus Endpoints
GET  /api/autofocus/config   # Auto-Focus Konfiguration
PUT  /api/autofocus/config   # Auto-Focus aktualisieren
```

---

## 🎯 Nächste Schritte

1. **Render Deploy** - Demo-Anmeldung Fix (is_ Spalte)
2. **Final Testing** - Alle Features testen
3. **Production Readiness** - Security & Monitoring