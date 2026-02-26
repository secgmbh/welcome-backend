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

### 2.2 Link/QR Code
- [x] Link/QR Code Cards existieren
- [ ] QR Code Download für Gäste

### 2.3 Profilverwaltung
- [x] Profil bearbeiten Seite existiert
- [x] Rechnungsdaten bearbeiten existiert (Backend PUT /api/auth/profile)

## Phase 3: Analytics (Medium Priority)

### 3.1 Analyse-Dashboard
- [ ] Detaillierte Statistiken zu Properties
- [ ] Buchungsübersicht & Export

### 3.2 Reporting
- [ ] PDF Export für Gäste-Guide
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

### 5.1 PDF Export für Gäste
- [ ] PDF Generierung für Guestview (Gäste-Guide als PDF)
- [ ] Template für PDF (LaTeX oder HTML-to-PDF)

### 5.2 QR Code Download
- [ ] Download Button für QR Codes
- [ ] QR Code als PNG herunterladen

### 5.3 Upsell-Management
- [ ] A/B-Tests für Upsell-Pakete
- [ ] Bundle-Erstellung
- [ ] Partner-Empfehlungen

### 5.4 Email Verification
- [ ] Verification Link in Registration E-Mail
- [ ] Backend Endpoint zum Verifizieren
