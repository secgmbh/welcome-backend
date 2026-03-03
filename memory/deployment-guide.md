# Deployment Guide - Welcome Link

## Übersicht

| Service | Provider | Repo |
|---------|----------|------|
| Frontend | Vercel | github.com/secgmbh/welcome-frontend |
| Backend | **Render** | github.com/secgmbh/welcome-backend |
| Database | Render PostgreSQL | - |

## ⚠️ WICHTIG: Render Deployment

**Render deployed NICHT automatisch bei jedem Push!**

### Manuell Deployen

1. Öffne: https://dashboard.render.com
2. Suche nach: `welcome-link-backend`
3. Klicke auf den Service
4. Klicke **Manual Deploy** → **Deploy latest commit**
5. Warte 2-3 Minuten bis Build fertig ist

### Deploy Status Prüfen

```bash
# API Status
curl -s "https://api.welcome-link.de/api/health" | jq

# Extras API (neue Endpoints)
curl -s "https://api.welcome-link.de/api/properties/17/extras" | jq

# Public API
curl -s "https://api.welcome-link.de/api/public/properties/QEJHEXP1QF" | jq
```

### Häufige Probleme

#### 1. Syntax-Fehler
```bash
# Vor dem Pushen prüfen:
cd backend
python3 -m py_compile server.py && echo "✅ Keine Syntax-Fehler"
```

#### 2. Import-Fehler
```bash
# Imports testen:
cd backend
python3 -c "import server" && echo "✅ Imports OK"
```

#### 3. Environment Variables
Fehlende ENV-Vars verursachen Runtime-Fehler:
- `SECRET_KEY` - JWT Secret
- `DATABASE_URL` - PostgreSQL Connection (auto von Render)
- `CORS_ORIGINS` - Allowed Origins

## Backend Struktur

```
welcome-backend/
├── backend/
│   ├── server.py          # Haupt-API (3800+ Zeilen)
│   ├── database.py        # DB Models
│   ├── requirements.txt   # Dependencies
│   └── alembic/          # Migrations
├── render.yaml           # Render Config
└── deploy.sh            # Manual Deploy Script
```

## Neue Endpoints Deployen

### 1. Code schreiben
```python
@api_router.get("/new-endpoint")
def new_endpoint():
    return {"status": "ok"}
```

### 2. Syntax prüfen
```bash
python3 -m py_compile backend/server.py
```

### 3. Commit & Push
```bash
git add backend/server.py
git commit -m "feat: add new endpoint"
git push origin main
```

### 4. Render Deploy
Manuell auf Dashboard oder warten auf Auto-Deploy

### 5. Verifizieren
```bash
curl -s "https://api.welcome-link.de/api/new-endpoint" | jq
```

## Database Migrations

### Neue Tabelle
```bash
# Migration Endpoint aufrufen
curl -X POST "https://api.welcome-link.de/api/debug/migrate-new-table"
```

### Seed Demo Data
```bash
# Login
TOKEN=$(curl -s -X POST https://api.welcome-link.de/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@welcome-link.de","password":"Demo123!"}' \
  | jq -r '.token')

# Seed
curl -X POST "https://api.welcome-link.de/api/debug/seed-extras/17" \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Deployment

Vercel deployed **automatisch** bei Push auf `main`.

```bash
cd welcome-frontend
git add .
git commit -m "feat: new feature"
git push origin main
# Vercel deployed automatisch
```

## Rollback

### Backend
1. Render Dashboard → Service
2. **Rollback** → Select previous deploy

### Frontend
1. Vercel Dashboard → Project
2. Deployments → Select previous → **Promote to Production**

## Monitoring

### Logs
- Render Dashboard → Service → **Logs**
- Vercel Dashboard → Project → **Deployments** → Logs

### Health Check
```bash
# Backend Health
curl -s "https://api.welcome-link.de/api/status" | jq

# Frontend
curl -s "https://www.welcome-link.de" -o /dev/null -w "%{http_code}"
```

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Project: `memory/render-deployment-fix.md`