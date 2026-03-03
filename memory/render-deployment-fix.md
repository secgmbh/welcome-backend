# 🔧 RENDER DEPLOYMENT FIX

## Problem
- Backend deployed nicht automatisch über GitHub
- Syntax-Fehler in `server.py` wurde behoben (Invoice-Funktion war unvollständig)
- Render muss manuell getriggert werden

## Lösung

### Option 1: Render Dashboard (Empfohlen)
1. Öffne: https://dashboard.render.com
2. Suche nach `welcome-link-backend`
3. Klicke auf **Manual Deploy** → **Deploy latest commit**
4. Warte bis Build fertig ist (ca. 2-3 Minuten)

### Option 2: Render CLI (falls installiert)
```bash
render deploy --service welcome-link-backend
```

### Option 3: Neuen Commit pushen (triggert manchmal Auto-Deploy)
```bash
cd welcome-backend
git commit --allow-empty -m "chore: trigger render"
git push origin main
```

## Status
- ✅ Syntax-Fehler behoben (Invoice PDF)
- ✅ Code committed und gepusht
- ⏳ Render muss deployen

## Nach dem Deployment

```bash
# 1. QR-Scans Tabelle erstellen
curl -X POST "https://api.welcome-link.de/api/debug/migrate-qr-scans"

# 2. Demo-Extras seeden
TOKEN=$(curl -s -X POST https://api.welcome-link.de/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@welcome-link.de","password":"Demo123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -X POST "https://api.welcome-link.de/api/debug/seed-extras/17" \
  -H "Authorization: Bearer $TOKEN"

# 3. Testen
curl -s "https://api.welcome-link.de/api/properties/17/extras"
```

## Was wurde gefixt

### server.py Zeile 3280
```python
# VORHER (unvollständig):
        # Tabelle
        data = [["Beschreibung", "Menge", "Einzelpreis", "Summe"]]


# ============== STRIPE PAYMENT ENDPOINTS ==============

# NACHHER (vollständig):
        # Tabelle
        data = [["Beschreibung", "Menge", "Einzelpreis", "Summe"]]
        
        # Items hinzufügen
        total = 0
        for item in items:
            line_total = float(item[2]) * item[3]
            total += line_total
            data.append([item[0], str(item[3]), f"€{float(item[2]):.2f}", f"€{line_total:.2f}"])
        
        # ... (komplette PDF-Generierung)
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren der Rechnung: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Generieren der Rechnung: {str(e)}")


# ============== STRIPE PAYMENT ENDPOINTS ==============
```

## Commits
- `e4d856c` - fix: complete invoice PDF generation function (was truncated)
- `0af9916` - chore: trigger render deployment
- `cdfb230` - chore: add setup script for demo extras