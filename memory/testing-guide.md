# Gästeseite Testing Guide

## Quick Test URLs

| Test | URL |
|------|-----|
| Gästeseite | https://www.welcome-link.de/guestview/QEJHEXP1QF |
| Dashboard | https://www.welcome-link.de/dashboard |
| Public API | https://api.welcome-link.de/api/public/properties/QEJHEXP1QF |
| Extras API | https://api.welcome-link.de/api/properties/17/extras |

## Test Credentials

| Feld | Wert |
|------|------|
| Email | demo@welcome-link.de |
| Password | Demo123! |
| Property ID | 17 |
| public_id | QEJHEXP1QF |

## Test Scenarios

### 1. WLAN Card
- [ ] WLAN Name wird angezeigt
- [ ] Passwort ist versteckt (••••••••)
- [ ] Eye-Button zeigt/versteckt Passwort
- [ ] Copy-Button kopiert Passwort
- [ ] Toast zeigt "kopiert!"

### 2. KeySafe Card
- [ ] Location wird angezeigt
- [ ] Code ist versteckt (••••)
- [ ] Eye-Button zeigt/versteckt Code
- [ ] Copy-Button kopiert Code
- [ ] Anleitung wird angezeigt

### 3. Google Maps
- [ ] Adresse wird angezeigt
- [ ] "In Maps öffnen" Button funktioniert
- [ ] Mobile: geo: URI öffnet Maps App
- [ ] Desktop: Google Maps öffnet

### 4. Extras Tab
- [ ] Extras werden geladen
- [ ] Preise werden angezeigt
- [ ] "Hinzufügen" Button funktioniert
- [ ] Warenkorb Badge zeigt Anzahl

### 5. Warenkorb
- [ ] Extras werden angezeigt
- [ ] Menge kann geändert werden
- [ ] Gesamtsumme stimmt
- [ ] "Zur Kasse" Button funktioniert

### 6. Checkout
- [ ] Name/Email Felder
- [ ] Payment Auswahl (Karte/PayPal/Bar)
- [ ] "Bezahlen" Button
- [ ] Bei Stripe/PayPal: Redirect

### 7. Contact Tab
- [ ] Telefon Link (tel:)
- [ ] Email Link (mailto:)
- [ ] WhatsApp Link (wa.me)

### 8. Error Handling
- [ ] Offline: Fehlermeldung
- [ ] Retry Button funktioniert
- [ ] Timeout nach 10s

### 9. i18n
- [ ] Browser auf DE: Deutsche Texte
- [ ] Browser auf EN: Englische Texte

## API Tests

```bash
# Public Property
curl -s "https://api.welcome-link.de/api/public/properties/QEJHEXP1QF" | jq

# Extras
curl -s "https://api.welcome-link.de/api/properties/17/extras" | jq

# Login
curl -s -X POST "https://api.welcome-link.de/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@welcome-link.de","password":"Demo123!"}' | jq

# Checkout (nach Deployment)
curl -s -X POST "https://api.welcome-link.de/api/checkout" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 17,
    "items": [{"extra_id": "test-id", "quantity": 1}],
    "guest_name": "Test Gast",
    "guest_email": "test@example.com",
    "payment_method": "cash"
  }' | jq
```

## Performance Tests

| Metrik | Ziel | Gemessen |
|--------|------|----------|
| Page Load | < 3s | ~1.2s |
| API Response | < 500ms | ~200ms |
| Time to Interactive | < 5s | ~2s |

## Browser Tests

- [ ] Chrome Desktop
- [ ] Firefox Desktop
- [ ] Safari Desktop
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)