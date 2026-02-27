# Phase 13: Global Statistics & Monitoring - TODO

## Features
- [ ] Globale Statistiken (Plattform-Umsatz, Anzahl der Hosts und Objekte)
- [ ] Nutzerverwaltung (Übersicht aller registrierten Firmen/Vermieter)
- [ ] Monitoring (Live-Feed der neuesten Buchungen über alle Unterkünfte hinweg)

## Backend API Endpoints (neu)

### Globale Statistiken
```
GET    /api/stats/global                # Globale Plattform-Statistiken
GET    /api/stats/host/{host_id}        # Host-spezifische Statistiken
```

### Nutzerverwaltung (Admin)
```
GET    /api/admin/users                 # Alle registrierten User
GET    /api/admin/users/{user_id}       # User Details
POST   /api/admin/users/{user_id}/ban   # User bannen
POST   /api/admin/users/{user_id}/verify # E-Mail verifizieren
```

### Monitoring
```
GET    /api/monitoring/booking-feed     # Live-Feed der neuesten Buchungen
GET    /api/monitoring/system-status    # System Status (DB, API, Cache)
```

### Global Stats Model
```python
class GlobalStats(BaseModel):
    total_hosts: int
    total_properties: int
    total_bookings: int
    total_revenue: float
    active_bookings_today: int
    completed_bookings_today: int
```

## Frontend UI (neu)

### Admin Dashboard
- `frontend/src/features/admin/AdminDashboard.jsx`
- Globale Statistiken (Karten)
- Nutzerverwaltungstabelle
- Live-Feed (Realtime aktualisieren)

### Admin User Management
- `frontend/src/features/admin/UserManagement.jsx`
- User-Tabelle mit Filtern
- E-Mail Verifizierung
- Ban/Deactivate User

## Integration
- `AdminDashboardPage.jsx`: Neue Tabs für Stats & Monitoring
