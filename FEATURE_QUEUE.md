# Feature Implementation Queue - aktueller Stand

## Phase 1: Core Auth + Guestview (High Priority) - FERTIG ✅
- [x] Guestview Page Frontend (GuestviewPage.jsx)
- [x] Guestview Page Backend (API Endpoints)
- [x] Email Service (SMTP Konfiguration)

## Phase 2: Host Dashboard (Medium Priority)

### 2.1 Unterkunftsverwaltung (Template)
- [ ] Template-Auswahl implementieren
- [ ] KI-Inhalts-Generator
- [ ] Upsell-Management mit A/B-Tests
- [ ] Bundle-Erstellung
- [ ] Partner-Empfehlungen
- [ ] Automatisierungsregeln

### 2.2 Link/QR Code - FERTIG ✅
- [x] Link/QR Code Cards existieren
- [x] QR Code Download für Gäste - FERTIG ✅

### 2.3 Profilverwaltung - FERTIG ✅
- [x] Profil bearbeiten Seite existiert
- [x] Rechnungsdaten bearbeiten existiert (Backend PUT /api/auth/profile)

## Phase 3: Analytics (Medium Priority)

### 3.1 Analyse-Dashboard
- [ ] Detaillierte Statistiken zu Properties
- [ ] Buchungsübersicht & Export

### 3.2 Reporting - FERTIG ✅
- [x] PDF Export für Gäste-Guide - FERTIG ✅
- [ ] Export Funktionen

## Phase 4: Missing Features - ERLEDIGT ✅

### 4.1 Dashboard Pages - ALLE EXISTIEREN ✅
- [x] SettingsPage.jsx
- [x] AdminDashboardPage.jsx
- [x] PropertyManagementPage.jsx
- [x] PropertyDetailPage.jsx

### 4.2 API Endpoints - ALLE EXISTIEREN ✅
- [x] PUT /api/properties/{id}
- [x] GET /api/properties/{id}
- [x] POST /api/properties
- [x] DELETE /api/properties/{id}
- [x] PUT /api/auth/profile
- [x] GET /api/auth/me

---

## Phase 5: Next Features (Medium Priority)

### 5.1 PDF Export für Gäste - FERTIG ✅
- [x] PDF Generierung für Guestview (Gäste-Guide als PDF)
- [x] Download Button für Guests

### 5.2 QR Code Download - FERTIG ✅
- [x] Download Button für QR Codes
- [x] QR Code als PNG herunterladen
- [x] QR Code cards in Guestview

### 5.3 Upsell-Management
- [ ] A/B-Tests für Upsell-Pakete
- [ ] Bundle-Erstellung
- [ ] Partner-Empfehlungen

### 5.4 Email Verification
- [ ] Verification Link in Registration E-Mail
- [ ] Backend Endpoint zum Verifizieren
