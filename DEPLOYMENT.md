# Welcome Link - Deployment Guide

## Übersicht

Willkommen bei der Welcome Link Deployment-Dokumentation. Dieses Dokument beschreibt den Deployment-Prozess für Produktion und Staging.

---

## Voraussetzungen

### Backend
- Python 3.11+
- FastAPI
- SQLite (Produktion: PostgreSQL empfohlen)
- SMTP Server für E-Mails

### Frontend
- Node.js 20+
- React 18
- Vite oder Create React App

### Infrastructure
- Render.com Account (oder ähnlicher Provider)
- Domain mit SSL-Zertifikat
- SMTP Service (z.B. SendGrid, Mailgun)

---

## Environment Variables

### Backend (.env)

```bash
# Required
SECRET_KEY=your-secret-key-min-32-characters
DATABASE_URL=sqlite:///./app.db

# SMTP Configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@welcome-link.de

# Optional
ENVIRONMENT=production
SENTRY_DSN=https://xxx@sentry.io/xxx
FRONTEND_URL=https://www.welcome-link.de
```

### Frontend (.env)

```bash
VITE_API_URL=https://api.welcome-link.de
```

---

## Deployment auf Render.com

### Backend Service

1. **Service erstellen**
   - Type: Web Service
   - Repository: `secgmbh/welcome-backend`
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables setzen**
   - Alle Variablen aus `.env` eintragen

3. **Auto-Deploy aktivieren**
   - Yes, für main Branch

### Frontend Service

1. **Service erstellen**
   - Type: Static Site
   - Repository: `secgmbh/welcome-frontend`
   - Branch: `main`
   - Build Command: `npm run build`
   - Publish Directory: `build`

2. **Environment Variables setzen**
   - `VITE_API_URL=https://api.welcome-link.de`

3. **Redirects konfigurieren**
   - Alle Routes zu `index.html` für SPA

---

## Cron Jobs

### Backup (täglich um 2:00 Uhr)
```bash
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Health Check (alle 5 Minuten)
```bash
*/5 * * * * /app/scripts/healthcheck.sh >> /var/log/healthcheck.log 2>&1
```

### Booking Reminders (täglich um 8:00 Uhr)
```bash
0 8 * * * curl -X POST https://api.welcome-link.de/api/cron/booking-reminders
```

### Guest Welcome (täglich um 10:00 Uhr)
```bash
0 10 * * * curl -X POST https://api.welcome-link.de/api/cron/guest-welcome
```

---

## API Endpoints

### Health Check
```
GET /api/health
→ {"status": "healthy", "version": "2.7.1", ...}
```

### API Info
```
GET /api/
→ {"message": "Welcome Link API", "version": "2.7.1"}
```

---

## Monitoring

### Sentry
- Error Tracking
- Performance Monitoring
- `SENTRY_DSN` Environment Variable setzen

### Health Check Script
- Prüft API alle 5 Minuten
- Prüft Frontend
- Prüft Demo Login
- Sendet Alerts bei Fehlern

---

## Backup

### Automatisches Backup
- Täglich um 2:00 Uhr
- 30 Tage Retention
- Komprimierte SQLite Datenbank

### Manuelles Backup
```bash
./scripts/backup.sh
```

---

## Rollback

### Backend Rollback
1. Render Dashboard öffnen
2. Service auswählen
3. "Manual Deploy" → Vorherigen Commit wählen

### Frontend Rollback
1. Render Dashboard öffnen
2. Static Site auswählen
3. "Rollback" → Vorheriges Deploy wählen

---

## Security Checklist

- [x] HTTPS erzwungen
- [x] Security Headers (CSP, X-Frame-Options, etc.)
- [x] Rate Limiting auf Auth Endpoints
- [x] JWT Token Expiration
- [x] Password Hashing (bcrypt)
- [x] Input Validation (Pydantic)
- [x] CORS konfiguriert

---

## Troubleshooting

### API nicht erreichbar
1. Render Service Status prüfen
2. Logs in Render Dashboard prüfen
3. Environment Variables prüfen

### E-Mails werden nicht gesendet
1. SMTP Credentials prüfen
2. SMTP Server Erreichbarkeit prüfen
3. Logs prüfen: `grep "E-Mail" /var/log/app.log`

### Frontend zeigt weiße Seite
1. Build Logs prüfen
2. `VITE_API_URL` prüfen
3. Browser Console auf Fehler prüfen

---

## Support

- GitHub Issues: https://github.com/secgmbh/welcome-backend/issues
- Email: support@welcome-link.de
- Docs: https://docs.welcome-link.de