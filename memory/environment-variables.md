# Environment Variables

## Frontend (.env)

```env
# API URL
VITE_API_URL=https://api.welcome-link.de

# PostHog Analytics (optional)
VITE_POSTHOG_KEY=phc_xxx
VITE_POSTHOG_HOST=https://eu.posthog.com

# Google Analytics (optional)
VITE_GA_MEASUREMENT_ID=G-xxx
```

## Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Auth
SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Stripe
STRIPE_SECRET_KEY=sk_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# PayPal
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx

# Email (optional)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=xxx

# Environment
ENVIRONMENT=production
CORS_ORIGINS=https://www.welcome-link.de
```

## GitHub Secrets

For CI/CD:

```env
VITE_API_URL=https://api.welcome-link.de
VITE_POSTHOG_KEY=phc_xxx
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
LHCI_GITHUB_APP_TOKEN=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx
```

## Render Environment

Backend on Render:

```env
# Auto-set by Render
RENDER=true
RENDER_SERVICE_ID=xxx

# Manual
DATABASE_URL=xxx (from Render PostgreSQL)
SECRET_KEY=xxx
STRIPE_SECRET_KEY=xxx
STRIPE_WEBHOOK_SECRET=xxx
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
CORS_ORIGINS=https://www.welcome-link.de
```

## Vercel Environment

Frontend on Vercel:

```env
VITE_API_URL=https://api.welcome-link.de
VITE_POSTHOG_KEY=phc_xxx
```

## Local Development

Create `.env.local` in frontend:

```env
VITE_API_URL=http://localhost:8000
```

Create `.env` in backend:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/welcome
SECRET_KEY=dev-secret-key-do-not-use-in-production
STRIPE_SECRET_KEY=sk_test_xxx
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```