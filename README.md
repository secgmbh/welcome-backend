# Welcome Link Backend

FastAPI-based REST API for the Welcome Link property management platform.

## Tech Stack

- **FastAPI 0.135.1** - Modern Python Web Framework
- **SQLAlchemy 2.0** - ORM for Database Operations
- **SQLite** - Development Database (PostgreSQL for Production)
- **PyJWT** - JWT Authentication
- **SlowAPI** - Rate Limiting
- **SMTP** - Email Integration
- **Sentry** - Error Tracking (Optional)

## Features

- JWT-based authentication with magic link support
- Property management with QR code generation
- Booking system with calendar integration
- Email templates for guest communication
- PayPal and Stripe webhook integration
- Cron job endpoints for automated tasks
- Rate limiting on auth endpoints
- Security headers (CSP, X-Frame-Options, etc.)
- Admin panel with full CRUD operations

## API Endpoints (60+)

### Auth
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/magic-link` - Magic link login
- `POST /api/auth/password-reset/request` - Request password reset
- `POST /api/auth/password-reset/confirm` - Confirm password reset

### Properties
- `GET /api/properties` - List properties
- `POST /api/properties` - Create property
- `GET /api/properties/{id}` - Get property
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property
- `GET /api/properties/{id}/extras` - Get property extras

### Bookings
- `GET /api/bookings` - List bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/{id}` - Get booking
- `GET /api/bookings/feed` - Live booking feed

### Webhooks
- `POST /api/webhooks/paypal` - PayPal webhook
- `POST /api/webhooks/stripe` - Stripe webhook

### Cron Jobs
- `POST /api/cron/booking-reminders` - Send booking reminders
- `POST /api/cron/guest-welcome` - Send guest welcome emails
- `POST /api/cron/checkout-followup` - Send checkout follow-ups

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key-min-32-chars"
export DATABASE_URL="sqlite:///./app.db"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="your-smtp-user"
export SMTP_PASSWORD="your-smtp-password"
export SMTP_FROM="noreply@welcome-link.de"

# Run development server
uvicorn server:app --reload

# Run tests
pytest
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT secret key (min 32 chars) | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `SMTP_HOST` | SMTP server host | Yes |
| `SMTP_PORT` | SMTP server port | Yes |
| `SMTP_USER` | SMTP username | Yes |
| `SMTP_PASSWORD` | SMTP password | Yes |
| `SMTP_FROM` | Sender email address | Yes |
| `SENTRY_DSN` | Sentry error tracking | No |
| `ENVIRONMENT` | Environment (development/production) | No |

## Deployment

The backend is deployed to Render with automatic deploys on push to main branch.

## License

Private - All rights reserved

## Support

For support, contact support@welcome-link.de