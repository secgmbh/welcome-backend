# Heartbeat Task List
# Check these periodically (every 30 min or so)

## Demo-Anmeldung Datenbank-Fix (Status: ERLEDIGT)

**Problem:** Demo-Anmeldung fehlgeschlagen mit `(psycopg2.errors.UndefinedColumn) column users.bra`

**Lösung (28.02.2026):**
- Fehlende Spalten in `User` model: `invoice_name`, `invoice_address`, `invoice_zip`, `invoice_city`, `invoice_country`, `invoice_vat_id`, `brand_color`, `logo_url`, `is_email_verified`, `email_verification_token`, `email_verification_token_expires`, `keysafe_location`, `keysafe_code`, `keysafe_instructions`
- Fehlende Modelle: `Scene`, `Extra`, `Bundle`, `BundleExtra`, `ABTest`, `Partner`, `SmartRule`, `Booking`, `Task`
- `PropertyStatsResponse` Model in `server.py` hinzugefügt
- Changes auf `nightly-improvements` Branch commited und pushed

**Status:** Deploy wurde gestartet, jetzt warten auf Feedback.

---

## Weekly Checks (rotate through)
- [ ] Git Status: Changes pushen?
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights