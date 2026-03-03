# Environment Variablen - Payment Integration

## Backend (.env)

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# PayPal
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
PAYPAL_MODE=sandbox  # oder live

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
EMAIL_FROM=noreply@welcome-link.de

# App
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
FRONTEND_URL=https://www.welcome-link.de
```

## Frontend (.env)

```bash
VITE_API_URL=https://api.welcome-link.de
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

## Stripe Setup

1. Account erstellen: https://dashboard.stripe.com
2. API Keys holen: Developers → API Keys
3. Webhook erstellen: Developers → Webhooks
   - URL: https://api.welcome-link.de/api/payment/stripe/webhook
   - Events: checkout.session.completed

## PayPal Setup

1. Account erstellen: https://developer.paypal.com
2. App erstellen: Dashboard → My Apps → Create App
3. Client ID & Secret holen
4. Sandbox vs Live Mode

## Test Cards (Stripe)

- Erfolgreich: 4242 4242 4242 4242
- Fehler: 4000 0000 0000 0002
- 3D Secure: 4000 0027 6000 3184

## PayPal Sandbox Accounts

- Käufer: sb-buyer@personal.example.com
- Verkäufer: sb-merchant@business.example.com