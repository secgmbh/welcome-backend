# Phase 17: Host-Spezifische Statistiken - TODO

## Features
- [ ] Host-spezifische Statistiken (Umsatz, Buchungen, Gäste pro Property)
- [ ] Statistiken als Diagramm visualisieren
- [ ] CSV Export für Statistiken

## Backend API Endpoints (neu)

### Host-Spezifische Statistiken
```
GET    /api/stats/host/{host_id}        # Host-spezifische Statistiken
GET    /api/stats/property/{id}         # Property-spezifische Statistiken
GET    /api/stats/bookings/export.csv   # Buchungen als CSV
```

### Property Stats Model
```python
class PropertyStats(BaseModel):
    property_id: str
    property_name: str
    total_bookings: int
    total_revenue: float
    total_guests: int
    avg_rating: Optional[float]
    last_booking: Optional[str]
```

## Frontend UI (neu)

### Property Statistics Dashboard
- `frontend/src/features/stats/PropertyStatsDashboard.jsx`
- Karten mit Statistiken (Umsatz, Buchungen, Gäste)
- Diagramm für Buchungen über Zeit
- CSV Export Button

### Statistics Page
- `frontend/src/pages/StatisticsPage.jsx`
- Host Stats Tab
- Property Stats Tab

## Integration
- `AnalyticsPage.jsx`: Neuer Tab für Host Stats

## Priorität: MEDIUM (Host-Experience Erweiterung)
