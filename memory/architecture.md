# Welcome Link - Gästeseite Premium

## Architektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │    Backend      │     │   Database      │
│   (React)       │────▶│   (FastAPI)     │────▶│   (PostgreSQL)  │
│   Vercel        │     │   Docker        │     │   Hostinger     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Stripe        │     │   PayPal        │
│   Payments      │     │   Payments      │
└─────────────────┘     └─────────────────┘
```

## API Endpoints

### Public (keine Authentifizierung)

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/api/public/properties/{public_id}` | GET | Property für Gästeseite |
| `/api/properties/{id}/extras` | GET | Extras einer Property |
| `/api/checkout` | POST | Checkout erstellen |
| `/api/checkout/{id}/invoice` | GET | PDF Rechnung |

### Authentifiziert

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/api/auth/login` | POST | Login |
| `/api/auth/register` | POST | Registrierung |
| `/api/auth/me` | GET | Aktueller User |
| `/api/properties` | GET/POST | Properties |
| `/api/properties/{id}` | GET/PUT/DELETE | Property |
| `/api/properties/{id}/extras` | POST | Extra erstellen |

### Payment

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/api/payment/stripe/create-session` | POST | Stripe Checkout |
| `/api/payment/stripe/webhook` | POST | Stripe Webhook |
| `/api/payment/paypal/create-order` | POST | PayPal Order |

## Datenbank Schema

### Properties

```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    address VARCHAR(500),
    public_id VARCHAR(20) UNIQUE,
    image_url VARCHAR(500),
    wifi_name VARCHAR(100),
    wifi_password VARCHAR(100),
    keysafe_location VARCHAR(200),
    keysafe_code VARCHAR(50),
    keysafe_instructions TEXT,
    checkin_time VARCHAR(10) DEFAULT '15:00',
    checkout_time VARCHAR(10) DEFAULT '11:00',
    host_phone VARCHAR(50),
    host_email VARCHAR(100),
    host_whatsapp VARCHAR(50),
    created_at TIMESTAMP
);
```

### Extras

```sql
CREATE TABLE extras (
    id VARCHAR(36) PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) DEFAULT 0,
    image_url VARCHAR(500),
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
);
```

### Checkouts

```sql
CREATE TABLE checkouts (
    id VARCHAR(36) PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    total DECIMAL(10,2) DEFAULT 0,
    guest_name VARCHAR(200),
    guest_email VARCHAR(200),
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP
);

CREATE TABLE checkout_items (
    id VARCHAR(36) PRIMARY KEY,
    checkout_id VARCHAR(36) REFERENCES checkouts(id),
    extra_id VARCHAR(36) REFERENCES extras(id),
    quantity INTEGER DEFAULT 1
);
```

## Frontend Komponenten

### GuestviewPage.jsx

Hauptkomponente für die Gästeseite mit:
- `WelcomeTab` - WLAN, KeySafe, Check-in/out
- `InfoTab` - Adresse, Notfall-Infos
- `ExtrasTab` - Extras mit Warenkorb
- `ContactTab` - Gastgeber-Kontakt

### Features

- **i18n** - Deutsch/Englisch
- **Copy-to-Clipboard** - WLAN, KeySafe
- **Google Maps** - geo: URI für Mobile
- **Warenkorb** - Add/Remove Extras
- **Checkout** - Name, Email, Payment
- **Loading Skeletons** - Bessere UX
- **Error Handling** - Retry-Button

## Deployment

### Frontend (Vercel)

```bash
cd welcome-frontend
npm run build
vercel --prod
```

### Backend (Docker)

```bash
cd welcome-backend
docker-compose build
docker-compose up -d
```

### Environment Variablen

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_xxx
PAYPAL_CLIENT_ID=xxx
SENDGRID_API_KEY=SG.xxx

# Frontend
VITE_API_URL=https://api.welcome-link.de
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

## Testing

### QR-Code Flow

1. Dashboard öffnen: https://www.welcome-link.de/dashboard
2. Property erstellen
3. QR-Code Tab öffnen
4. QR-Code scannen
5. Gästeseite sollte laden

### Checkout Flow

1. Gästeseite öffnen
2. Extras Tab → Extras hinzufügen
3. Warenkorb → Zur Kasse
4. Name/Email eingeben
5. Payment wählen
6. Bezahlen
7. PDF Rechnung herunterladen

## Support

- **Email:** support@welcome-link.de
- **Docs:** https://docs.welcome-link.de
- **Status:** https://status.welcome-link.de