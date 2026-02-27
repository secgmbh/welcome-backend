# Phase 10: Advanced Guest Features - TODO

## Features
- [ ] Interaktiver Walkthrough (Schritt-für-Schritt Navigation)
- [ ] Echtzeit-Feedback (Daumen-hoch/runter pro Seite)
- [ ] Seamless Shopping (Warenkorb)
- [ ] Trinkgeld-Funktion (Prozentsätze im Checkout)

## Backend API Endpoints (neu)

### Echtzeit-Feedback
```
POST   /api/feedback                    # Neues Feedback erstellen
GET    /api/feedback?property_id={id}   # Feedback für Property holen
```

### Trinkgeld-Konfiguration
```
GET    /api/tipping-config              # Trinkgeld-Konfiguration holen
POST   /api/tipping-config              # Trinkgeld-Konfiguration aktualisieren
```

### Warenkorb (Shopping Cart)
```
GET    /api/cart                        # Warenkorb holen
POST   /api/cart                        # Artikel zum Warenkorb hinzufügen
PUT    /api/cart/{item_id}              # Artikel im Warenkorb aktualisieren
DELETE /api/cart/{item_id}              # Artikel aus Warenkorb entfernen
POST   /api/cart/checkout               # Checkout starten
```

## Frontend UI (neu)

### Interaktiver Walkthrough
- `frontend/src/features/guestview/Walkthrough.jsx`
- Schritt-für-Schritt Navigation durch Informationsszenen
- Navigation Buttons (Zurück, Weiter)

### Echtzeit-Feedback
- `frontend/src/features/guestview/Feedback.jsx`
- Daumen-hoch/runter pro Seite
- Feedback Modal öffnet bei negativem Feedback

### Seamless Shopping
- `frontend/src/features/guestview/Cart.jsx`
- Warenkorb mit Mengenwahl
- Bestandsprüfung
- Checkout-Schaltfläche

### Trinkgeld-Konfigurator
- `frontend/src/features/guestview/TippingConfig.jsx`
- Prozentsätze konfigurieren
- Vordefinierte Tipp-Buttons

## Integration
- `GuestviewPage.jsx`: Tab-Navigation umschalten
- `BookingForm.jsx`: Warenkorb & Trinkgeld integrieren
