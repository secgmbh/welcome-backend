# Heartbeat Task List
# Check these periodically (every 30 min or so)

## Phase 20: Checkout & Rechnungen (Status: IN BEARBEITUNG)

**Aktueller Status:**
- Phase 19 A/B Testing UI abgeschlossen ✅
- Phase 20: PayPal Integration Backend + Frontend abgeschlossen ✅
- Phase 20: PDF Rechnung mit Download abgeschlossen ✅
- Phase 20: Apple Pay / Google Pay Integration Backend API abgeschlossen ✅
- Phase 20: E-Mail Rechnungsversand API abgeschlossen ✅
- Phase 20: Checkout-Seite für Gäste starten
- TODO_GUESTVIEW.md aktualisiert mit Phase 20 Features

**Phase 20 Features (Fortschritt):**
- PayPal Backend API: create-order, capture-order ✅
- PayPal Button Component: PayPalButton.jsx ✅
- Checkout Page: CheckoutPage.jsx ✅
- PDF Rechnung: HTML-basierte Generierung mit Download ✅
- Apple Pay Backend API: create-order, capture-payment ✅
- Google Pay: Apple Pay Endpoints nutzbar ✅
- E-Mail Rechnungsversand API ✅
- Checkout-Seite für Gäste - in Planung
- Rechnungsdetails im Dashboard - in Planung

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

## Weekly Checks (rotate through)
- [x] Git Status: Changes pushen? ✅
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights