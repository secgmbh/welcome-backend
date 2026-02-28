# Heartbeat Task List
# Check these periodically (every 30 min or so)

## 🚨 ZWINGENDE AKTION NÖTIG - Demo-Anmeldung kaputt

**Problem:** Demo-Anmeldung fehlgeschlagen mit `(psycopg2.errors.UndefinedColumn) column users.bra`

**Status:** Code-Fix ist commited und pushed auf `nightly-improvements` Branch.

**Root Cause:** Es gibt ZWEI unterschiedliche `database.py` Dateien:
1. `/data/.openclaw/workspace/database.py` - Hauptdatei
2. `/data/.openclaw/workspace/welcome-backend/backend/database.py` - Backend-Version

Der Server importiert `welcome-backend/backend/database.py`.

**Lösung:**
- Alle fehlenden Spalten (`invoice_name`, `invoice_address`, `brand_color`, `is_email_verified`, etc.) zu `User` model hinzugefügt
- Alle fehlenden Modelle (`Scene`, `Extra`, `Bundle`, `BundleExtra`, `ABTest`, `Partner`, `SmartRule`, `Booking`, `Task`) hinzugefügt
- `PropertyStatsResponse` Model in `server.py` hinzugefügt

**Was jetzt tun:**
1. Deploy zur Render-Instanz manuell starten (nightly-improvements Branch)
2. Oder `gateway restart` ausführen (wenn systemd verfügbar ist)
3. Demo-Anmeldung testen nach Deploy

## Weekly Checks (rotate through)
- [x] Git Status: Changes pushen? (nightly-improvements)
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights