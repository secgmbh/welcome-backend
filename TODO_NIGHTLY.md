# Welcome-Link Nightly Improvement Queue

Dies ist die Queue für Night Mode Runs (22:30-04:00, alle 30min).

## Features Check - Stand 26.02.2026

### ✅ Bereits Implementiert
1. **Analytics System** - PostHog mit 20+ Events
2. **SEO** - Meta Tags, Structured Data, Sitemap
3. **PWA** - Service Worker, Manifest, Offline Support
4. **i18n** - DE/EN Multi-Language
5. **Language Switcher** - Flaggen-UI mit Dark Mode
6. **PDF Export** - HTML zu PDF, Gäste-Guide
7. **QR Code Generator** - Property QR Codes mit Logo
8. **Lazy Loading** - Bilder, Routes, Components
9. **Security** - CSP, reCAPTCHA
10. **Rechnungssystem** - Admin Dashboard mit Invoice Management

### ⚠️ Fehlendes Feature
1. **Guestview Page** - Seite die Gäste sehen nach Login
   - Property Übersicht
   - Check-in/out Info
   - Wi-Fi Credentials
   - House Rules
   - Amenity Details
   - QR Code Download

## Priorisierte Tasks (Feature-Related)

### High Priority
1. **Guestview Page frontend** - React Komponente für Gäste
2. **Guestview Page backend** - API Endpoint `/api/guestview/{property_id}`
3. **Email Service** - SMTP Konfiguration finalisieren (Info@welcome-link.de)

### Medium Priority
4. **Error Boundary** - Integration mit Sentry/LogRocket
5. **Performance Monitoring** - Lighthouse Scores verbessern
6. **Loading States** - Bessere Feedback beim Laden

### Low Priority
7. **Type Safety** - Mehr TypeScript in Frontend
8. **Code Formatting** - Black/Ruff, Prettier
9. **API Documentation** - OpenAPI Spec

## Nightly Checklist (vor jedem Run)

- [ ] Branch: nightly-improvements
- [ ] Lock File: Kein laufender Process
- [ ] Zeitfenster: 22:30-04:00
- [ ] Files changed: ≤10
- [ ] Build/lint: Keine Fehler
- [ ] Commit message: `nightly: <description>`

## Documentation
- See `HEARTBEAT.md` for execution rules
- See `nightly-lock.sh` for lock mechanism
