# Heartbeat Task List
# Check these periodically (every 30 min or so)

## Phase 20: Checkout & Rechnungen (Status: 100% COMPLETE ✅)

**Aktueller Status:**
- Phase 19 A/B Testing UI abgeschlossen ✅
- Phase 20: PayPal Integration Backend + Frontend abgeschlossen ✅
- Phase 20: PDF Rechnung mit Download abgeschlossen ✅
- Phase 20: Apple Pay / Google Pay Integration Backend API abgeschlossen ✅
- Phase 20: E-Mail Rechnungsversand API abgeschlossen ✅
- Phase 20: Checkout-Seite für Gäste (frontend) abgeschlossen ✅
- Phase 21: Rechnungsdetails im Dashboard + Nutzerverwaltung Backend + Frontend + Live-Feed + AutoFocus ✅
- Phase 22: Live-Feed UI abgeschlossen ✅
- TODO_GUESTVIEW.md aktualisiert mit Phase 21 Features

**Phase 20 Features (100% Complete):**
- PayPal Backend API: create-order, capture-order ✅
- PayPal Button Component: PayPalButton.jsx ✅
- Checkout Page: CheckoutPage.jsx ✅
- PDF Rechnung: HTML-basierte Generierung mit Download ✅
- Apple Pay Backend API: create-order, capture-payment ✅
- Google Pay: Apple Pay Endpoints nutzbar ✅
- E-Mail Rechnungsversand API ✅
- Checkout-Seite für Gäste: Route `/checkout/:bookingId` ✅

**Changelog (Phase 20):**
- 2026-02-28: PayPal Integration + PDF Rechnung + Apple Pay + Email + Checkout Seite

**Backend API Summary (Phase 20):**
- `/api/paypal/create-order`
- `/api/paypal/capture-order`
- `/api/bookings/{id}/invoice` (PDF base64)
- `/api/bookings/{id}/invoice/download`
- `/api/apple-pay/create-order`
- `/api/apple-pay/capture-payment`
- `/api/invoice/email`

**Changelog:**
- PDF Rechnung mit base64-HTML-Integration für Druck
- Download-Endpoint `/api/bookings/{id}/invoice/download`

## Phase 21: Dashboard Erweiterungen (Status: 100% COMPLETE)
- Rechnungsdetails im Dashboard - abgeschlossen ✅
- Nutzerverwaltung Backend API - abgeschlossen ✅
- Nutzerverwaltung Frontend UI - abgeschlossen ✅
- Live-Feed Buchungen - abgeschlossen ✅
- AutoFocus API Fix - abgeschlossen ✅

## Phase 22: Admin Features (Status: IN BEARBEITUNG)
- Nutzerverwaltung (alle registrierte Firmen) - Backend API ✅
- Live-Feed Buchungen - Backend API ✅
- AutoFocus API Fix - abgeschlossen ✅
- Live-Feed UI - abgeschlossen ✅

## Weekly Checks (rotate through)
- [x] Git Status: Changes pushen? ✅
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights