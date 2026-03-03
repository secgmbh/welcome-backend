# Welcome Link

**Digitale Gästemappe für Ferienunterkünfte**

## Features

- **QR-Code Check-in** - Gäste scannen QR-Code und erhalten alle Informationen
- **Premium Design** - Glass Morphism, Animationen, Dark Mode
- **PWA Support** - Offline-fähig, installierbar
- **Multi-Language** - Deutsch und Englisch
- **Extras & Buchungen** - Zusatzleistungen direkt buchen
- **Analytics** - QR-Scans, Buchungen, Umsatz
- **Payment** - Stripe und PayPal Integration

## Tech Stack

### Frontend
- React 18 mit Vite
- TailwindCSS für Styling
- React Router für Navigation
- React Query für Data Fetching
- PWA mit Service Worker

### Backend
- Python FastAPI
- PostgreSQL Datenbank
- Stripe & PayPal Payments
- JWT Authentication

## Quick Start

```bash
# Clone repository
git clone https://github.com/secgmbh/welcome-link.git
cd welcome-link

# Start with Docker
docker-compose up -d

# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_POSTHOG_KEY=phc_xxx
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Backend (.env)
```env
DATABASE_URL=postgresql://welcome:welcome@db:5432/welcome
SECRET_KEY=your-secret-key-min-32-chars
STRIPE_SECRET_KEY=sk_xxx
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
```

## Project Structure

```
welcome-link/
├── frontend/           # React Frontend
│   ├── src/
│   │   ├── components/ # Reusable Components
│   │   ├── features/   # Feature Modules
│   │   ├── hooks/      # Custom Hooks
│   │   ├── lib/        # Utilities
│   │   └── pages/      # Page Components
│   └── public/         # Static Assets
├── backend/            # FastAPI Backend
│   ├── server.py       # Main Application
│   ├── models.py       # Database Models
│   ├── webhooks.py     # Webhook Handlers
│   └── tests/          # Test Suite
└── memory/             # Documentation
```

## API Endpoints

### Public
- `GET /api/public/properties/:public_id` - Gästeseite Daten

### Auth
- `POST /api/auth/register` - Registrierung
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Aktueller User

### Properties
- `GET /api/properties` - Eigene Unterkünfte
- `POST /api/properties` - Neue Unterkunft
- `PUT /api/properties/:id` - Unterkunft bearbeiten

### Extras
- `GET /api/properties/:id/extras` - Extras auflisten
- `POST /api/properties/:id/extras` - Extra erstellen

### Checkout
- `POST /api/checkout` - Neue Bestellung
- `GET /api/checkout/:id/invoice` - PDF Rechnung

## Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Render)
1. GitHub Repository verbinden
2. Environment Variables setzen
3. Deploy

## Demo

- **Frontend:** https://www.welcome-link.de
- **Gästeseite:** https://www.welcome-link.de/guestview/QEJHEXP1QF
- **Login:** demo@welcome-link.de / Demo123!

## License

MIT License - (c) 2026 SEC GmbH