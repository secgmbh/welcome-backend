# Heartbeat Task List
# Check these periodically (every 30 min or so)

## 🚨 ZWINGENDE AKTION NÖTIG - Demo-Anmeldung kaputt

**Problem:** Demo-Anmeldung fehlgeschlagen mit `(psycopg2.errors.UndefinedColumn) column users.bra`

**Status:** Code-Fix ist commited und pushed. Aber: Die Hauptdatei `/database.py` importiert nicht `welcome-backend/backend/database.py`.

**Root Cause:** Es gibt ZWEI unterschiedliche `database.py` Dateien:
1. `/data/.openclaw/workspace/database.py` - Hauptdatei mit allen Spalten
2. `/data/.openclaw/workspace/welcome-backend/backend/database.py` - Submodule-Version

Der Server importiert `welcome-backend/backend/database.py` (nicht die Hauptdatei).

**Was jetzt tun:**
1. `gateway restart` ausführen (wenn systemd verfügbar ist)
2. Oder manuell Deploy auf Render starten
3. Demo-Anmeldung testen nach Deploy

## Weekly Checks (rotate through)
- [ ] Git Status: Changes pushen?
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights