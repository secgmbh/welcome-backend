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
- [ ] POST /auth/guestview-token (einzigartige URL generieren) - TODO
- [ ] GET /auth/guestview/{token} (passwortlose Ansicht) - TODO

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

### Phase 2: Host Dashboard (Medium Priority) - TODO
4. Unterkunftsverwaltung (Template)
5. Link/QR Code
6. Profilverwaltung

### Phase 3: Analytics (Medium Priority) - TODO
7. Analyse-Dashboard
8. Buchungsübersicht & Export

## Design (gemäß MVP-Liste) ✅
- Kartenbasiertes Layout
- Hell/Dunkelmodus
- PT Sans Schriftart
- lucide-react Icons
- Button-Hierarchie: primary, secondary, ghost, destructive, icon
