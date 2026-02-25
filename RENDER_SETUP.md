# Render Setup Anleitung - Welcome Link Backend

## E-Mail Konfiguration (SMTP)

Gehe zu: https://dashboard.render.com/web/srv-cj31u5l4t3u0g9k3g0mg → Settings → Secrets

Füge diese Secrets hinzu:

| Secret Name | Wert |
|-------------|------|
| `SMTP_USER` | `info@welcome-link.de` |
| `SMTP_PASSWORD` | `td2dfTR87tFiw2Wg` |

## WICHTIG: Nach dem Hinzufügen der Secrets

1. Klick auf **Manual Deploy** → **Deploy latest commit**
2. Warte bis Build fertig ist
3. Prüfe die Logs für SMTP-Verbindungsfehler

## Datenbank Konfiguration

Die PostgreSQL Datenbank wird von Render automatisch eingetragen:
- Host: `jts0.your-database.de`
- Database: `npuqdy_db1`
- User: `npuqdy_1`
- Port: `5432`

Die Verbindungs-URL wird als `DATABASE_URL` automatisch gesetzt.

## Demo & Admin User

Die Credentials sind im Code hardcoded (nicht in Environment):
- **Demo:** demo@welcome-link.de / demo123
- **Admin:** admin@welcome-link.de / admin123

Diese sind **NICHT öffentlich sichtbar** - nur im Code für interne Tests.

## Test E-Mail Versand

Sobald SMTP konfiguriert ist, teste mit:
1. Registrierung mit einer echten E-Mail
2. Magic Link Anfrage

## Wenn E-Mails nicht gehen

Prüfe in den Render Logs:
- SMTP-Verbindungsfehler?
- Falscher Port?
- Authentifizierungsfehler?

Mögliche Lösungen:
1. Port 465 (SSL) statt 587 (TLS)
2. `mail.your-server.de` statt `smtp.your-server.de`
3. credentials prüfen auf Tippfehler
