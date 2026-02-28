# Heartbeat Task List
# Check these periodically (every 30 min or so)

## 🚨 ZWINGENDE AKTION NÖTIG - Demo-Anmeldung kaputt

**Problem:** Demo-Anmeldung fehlgeschlagen mit `(psycopg2.errors.UndefinedColumn) column users.bra`

**Status:** Code-Fix ist commited und pushed, aber **Live-Server muss neu gestartet werden**.

**Was ist fixt:**
- Fehlende `invoice_`, `brand_`, `keysafe_` Spalten in User-Modell
- Fehlende Modelle: `Scene`, `Extra`, `Bundle`, `BundleExtra`, `ABTest`, `Partner`, `SmartRule`, `Booking`, `Task`
- Fehlendes `PropertyStatsResponse`-Model in `server.py`

**Was jetzt tun:**
1. Deploy zur Render-Instanz manuell starten
2. Oder `gateway restart` ausführen (wenn systemd verfügbar ist)
3. Demo-Anmeldung testen nach Deploy

---

## Weekly Checks (rotate through)
- [ ] Git Status: Changes pushen?
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights
