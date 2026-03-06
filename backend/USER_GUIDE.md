# Welcome Link - User Guide

## Schnellstart

### Demo-Zugang

Testen Sie Welcome Link mit unserem Demo-Account:

- **URL:** https://www.welcome-link.de
- **E-Mail:** `demo@welcome-link.de`
- **Passwort:** `Demo123!`

---

## Features

### 1. Dashboard

Das Dashboard ist Ihre zentrale Übersicht:

- **Properties:** Verwalten Sie Ihre Ferienwohnungen
- **Bookings:** Übersicht aller Buchungen
- **Analytics:** Statistiken und Umsatzzahlen
- **QR-Codes:** Generieren Sie Guestview-Links

### 2. Property Management

#### Property erstellen

1. Klicken Sie auf "Neue Property"
2. Füllen Sie die Basis-Daten aus:
   - Name der Unterkunft
   - Beschreibung
   - Adresse
   - Check-in/Check-out Zeiten

#### WiFi & Keysafe

- **WLAN-Name:** Für Ihre Gäste sichtbar
- **WLAN-Passwort:** Sicher hinterlegt
- **Keysafe-Code:** Für Selbst-Check-in

### 3. Guestview

Die Guestview ist die digitale Gäste-Mappe:

- WLAN-Daten
- Hausregeln
- Umgebungstipps
- Extras buchbar

#### QR-Code generieren

1. Gehen Sie zur Property
2. Klicken Sie auf "Guestview-Link"
3. QR-Code wird automatisch erstellt
4. Drucken oder digital teilen

### 4. Scenes (Info-Seiten)

Erstellen Sie informative Seiten für Ihre Gäste:

1. **Willkommen** - Begrüßungstext
2. **WLAN & Internet** - Zugangsdaten
3. **Hausregeln** - Wichtige Hinweise
4. **Umgebung** - Restaurants, Aktivitäten

### 5. Extras & Services

Bieten Sie Zusatzleistungen an:

- 🍳 Frühstück
- 🚴 Fahrradverleih
- 💆 Wellness & Massage
- 🚗 Shuttle Service
- 🐕 Haustier-Option

### 6. Buchungen

#### Buchungsübersicht

Alle Buchungen mit Status:
- **Pending** - Warten auf Bestätigung
- **Confirmed** - Bestätigt
- **Completed** - Abgeschlossen
- **Cancelled** - Storniert

#### Kalender-Export

Exportieren Sie Buchungen als `.ics` für:
- Google Calendar
- Apple Calendar
- Outlook

### 7. Analytics

#### Statistiken

- Buchungen pro Monat
- Umsatzentwicklung
- Durchschnittlicher Buchungswert
- Belegungsrate

#### Export

- **CSV** - Für Excel/Numbers
- **PDF** - Für Dokumentation

---

## API Integration

Für Entwickler:

### Endpoints

```
POST /api/auth/login          # Login
GET  /api/properties          # Properties
GET  /api/bookings            # Buchungen
GET  /api/scenes              # Info-Seiten
GET  /api/guestview/{token}   # Gäste-Ansicht
```

### Beispiel

```bash
# Login
curl -X POST https://api.welcome-link.de/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@welcome-link.de","password":"Demo123!"}'

# Response
{"token": "eyJhbG...", "user": {...}}
```

---

## Tipps

### QR-Code platzieren

- An der Eingangstür
- Auf dem Kühlschrank
- Im Gäste-Ordern

### Szenen nutzen

- Halten Sie Texte kurz
- Nutzen Sie Emojis für bessere Lesbarkeit
- Aktualisieren Sie Tipps regelmäßig

### Extras anbieten

- Preiswerte Optionen erhöhen die Zufriedenheit
- Klare Beschreibungen vermeiden Missverständnisse
- Saisonale Extras anbieten

---

## Support

- **E-Mail:** support@welcome-link.de
- **Demo:** https://www.welcome-link.de
- **API Docs:** https://api.welcome-link.de/docs (nur Development)

---

## Security

- Passwörter werden mit bcrypt verschlüsselt
- JWT-Tokens für Authentifizierung
- Rate Limiting auf Auth-Endpoints
- Security Headers (CSP, X-Frame-Options, HSTS)

---

© 2026 Welcome Link - Digitale Gäste-Mappe