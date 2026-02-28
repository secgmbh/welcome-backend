# Heartbeat Task List
# Check these periodically (every 30 min or so)

## Demo-Anmeldung Datenbank-Fix (Status: IN BEARBEITUNG)

**Problem:** Demo-Anmeldung fehlt mit `(psycopg2.errors.UndefinedColumn) column users.bra`

**Lösung (28.02.2026):**
- Fehlende Spalten in `User` model: `invoice_name`, `invoice_address`, `invoice_zip`, `invoice_city`, `invoice_country`, `invoice_vat_id`, `brand_color`, `logo_url`, `is_email_verified`, `email_verification_token`, `email_verification_token_expires`, `keysafe_location`, `keysafe_code`, `keysafe_instructions`
- Fehlende Modelle: `Scene`, `Extra`, `Bundle`, `BundleExtra`, `ABTest`, `Partner`, `SmartRule`, `Booking`, `Task`
- `PropertyStatsResponse` Model in `server.py` hinzugefügt
- Changes auf `nightly-improvements` Branch commited und pushed

**Root Cause:** Es gab ZWEI verschiedene `database.py` Dateien (Hauptverzeichnis vs. welcome-backend/backend). Der Server nutzt die Datei im welcome-backend Ordner.

**Status:** Alembic Migration `75d1541dc08a` hinzugefügt, die fehlenden Spalten auf der Datenbank hinzufügt. Changes commited und pushed.

**Was die Migration tut:**
- `is_email_verified` (Boolean)
- `email_verification_token` (String 64)
- `email_verification_token_expires` (DateTime)
- `brand_color` (String 7)
- `logo_url` (String 500)
- `keysafe_location` (String 500)
- `keysafe_code` (String 50)
- `keysafe_instructions` (Text)

**Nächster Schritt:** Oleg muss einen manuellen Deploy auf Render ausführen, damit die Migration ausgeführt wird.

## Weekly Checks (rotate through)
- [ ] Git Status: Changes pushen?
- [ ] TODOs prüfen und aufräumen
- [ ] Logs checken für Fehler

## Memory Maintenance
- [ ] Review `memory/` files and update `MEMORY.md` with insights