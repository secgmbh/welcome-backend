# Guestview MVP Implementation - Status 26.02.2026

## Backend (Python/FastAPI) - welcome-backend/

### 1. Datenbank Modelle ✅
- [x] DBUser (mit is_email_verified, invoice_* Feldern)
- [x] DBProperty (Unterkünfte)
- [x] DBBooking (Buchungen)
- [x] DBExtra (Upsells)
- [x] DBScene (Informationsschritte)

### 2. API Endpoints ✅
- [x] POST /auth/register (mit Rechnungsdaten)
- [x] POST /auth/login (Email + Passwort)
- [x] GET /auth/me (Profildaten)
- [x] PUT /auth/profile (Rechnungsdaten bearbeiten)
- [x] GET /api/properties (Liste der Unterkünfte)
- [x] POST /api/properties (Neue Unterkunft erstellen)
- [x] DELETE /api/properties/{id} (Unterkunft löschen)
- [x] POST /api/guestview-token (einzigartige URL generieren)
- [x] GET /api/guestview/{token} (passwortlose Ansicht)

### 3. E-Mail Service ⚠️
- [x] SMTP Fallback (info@welcome-link.de)
- [x] Email senden funktioniert
- [ ] Email Verification Link implementieren - TODO
- [ ] Password Reset (optional)

## Frontend (React) - welcome-frontend/

### 1. Auth Pages ✅
- [x] RegisterPage (mit Rechnungsdaten)
- [x] LoginPage (Email + Passwort)
- [x] EmailVerifiedPage (wenn nicht verifiziert)
- [x] ProfilePage (Rechnungsdaten bearbeiten)

### 2. Host Dashboard ⚠️
- [x] Tab-Navigation
- [x] Unterkunftskarten (Liste)
- [ ] Template-Auswahl - TODO
- [ ] Link/QR Code Cards - TODO
- [ ] Analyse-Dashboard - TODO
- [ ] Buchungsübersicht & Export - TODO

### 3. Unterkunfts-Editor ⚠️
- [ ] Drag-and-Drop Szenen-Editor - TODO
- [ ] KI-Inhalts-Generator - TODO
- [ ] Upsell-Management mit A/B-Tests - TODO
- [ ] Bundle-Erstellung - TODO
- [ ] Partner-Empfehlungen - TODO
- [ ] Automatisierungsregeln - TODO

### 4. Guestview Page (Gäste-Seite) ⚠️
- [ ] Passwortlose URL /guestview/{token} - TODO
- [ ] properties/{id} Seite für Gäste - TODO
- [ ] Info-Szenen (Drag-and-Drop sortierbar) - TODO
- [ ] Amenity Anzeige - TODO
- [ ] QR Code Download - TODO

## MVP Priorität

### Phase 1: Core Auth + Guestview (High Priority) - TODO
1. Guestview Token API
2. Passwortlose Gästeanmeldung
3. Properties Seite für Gäste

## Phase 2: Host Dashboard (Medium Priority) - **27.02.2026**
- [x] Unterkunftsverwaltung (Template) - ✅ implemented
- [x] Link/QR Code Cards - ✅ implemented
- [x] Guestview Generator im Dashboard - ✅ implemented
- [x] Template-Auswahl für Unterkünfte - ✅ implemented
- [x] Property Template Selector - ✅ implemented
- [x] New Property Wizard - ✅ implemented

## Phase 3: Analytics (Medium Priority) - **27.02.2026**
- [x] Analyse-Dashboard - ✅ implemented
- [x] Property QR Code Cards mit Download - ✅ implemented
- [x] Guestview Link Generator - ✅ implemented

### Phase 3 UI Components
- [x] AnalyticsTab - Statistik-Karten in Dashboard
- [x] PropertyStats - Statistiken für jede Property
- [x] QRCodeCard - QR Code Anzeige mit Download
- [x] GuestviewLinkCard - Guestview Link Karte mit Copy-Funktion

## Phase 4: Profilverwaltung & Buchungen (Medium Priority) - **27.02.2026**
- [ ] Profilverwaltung - TODO
- [ ] Buchungsübersicht & Export - TODO
- [ ] Booking API Integration - TODO
- [ ] Booking Formular für Gäste - TODO

### Phase 4 Tasks
1. ProfilePage - Rechnungsdaten bearbeiten (Frontend)
2. BookingDashboard - Buchungsübersicht im Dashboard
3. Booking API - GET/POST /api/bookings
4. Booking Form - Gast-Buchungsformular

## Design (gemäß MVP-Liste) ✅
- Kartenbasiertes Layout
- Hell/Dunkelmodus
- PT Sans Schriftart
- lucide-react Icons
- Button-Hierarchie: primary, secondary, ghost, destructive, icon
