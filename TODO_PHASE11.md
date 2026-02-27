# Phase 11: Checkout & Rechnungen - TODO

## Features
- [ ] Checkout-Simulation (PayPal/Apple/Google Pay Visuals)
- [ ] Digitale Rechnung (sofort nach Buchung)
- [ ] PDF-Export als sofortiger Download

## Backend API Endpoints (neu)

### Checkout & Buchung
```
POST   /api/checkout                    # Checkout starten (Vorab-Validierung)
POST   /api/checkout/process            # Buchung endgültig abschließen
GET    /api/bookings/{id}/invoice       # Rechnung als PDF holen
```

### Booking Model Erweiterung
```python
class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    guest_name = Column(String(200))
    guest_email = Column(String(200))
    guest_phone = Column(String(50))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    guests = Column(Integer)
    message = Column(Text)
    total_price = Column(Float)
    tipping_percentage = Column(Integer, default=0)
    tipping_amount = Column(Float, default=0)
    status = Column(String(50), default='pending')  # pending, confirmed, cancelled
    payment_method = Column(String(50))  # paypal, apple_pay, google_pay, none
    invoice_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## Frontend UI (neu)

### Checkout-Simulation
- `frontend/src/features/bookings/CheckoutSimulation.jsx`
- Zahlungsmethoden: PayPal, Apple Pay, Google Pay
- Visuelle Feedbacks für成功/fehlgeschlagene Zahlung
- Sicherheits-Hinweise (SSL, verschlüsselt)

### Digital Rechnung
- `frontend/src/features/bookings/InvoiceGenerator.jsx`
- Echtzeit-Generierung nach Buchung
- PDF-Download sofort verfügbar
- Rechnungsdetails: Buchungsnummer, Preise, Extras, Trinkgeld

## Integration
- `BookingForm.jsx`: Checkout-Simulation integrieren
- `GuestviewPage.jsx`: Rechnung nach Buchung anzeigen

## Priorität: HIGH (MVP-Finisher)
