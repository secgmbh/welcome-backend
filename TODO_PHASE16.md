# Phase 16: Kalender-Sync (.ics Export) - TODO

## Features
- [ ] Szenen als .ics Kalender exportieren
- [ ] Termine für Szenen exportieren
- [ ] Kalender-Abonnement für Gäste

## Backend API Endpoints (neu)

### Kalender Export
```
GET    /api/scenes/export/ics
GET    /api/properties/{id}/scenes/export/ics
```

### .ics Export Response
```
Content-Type: text/calendar
Content-Disposition: attachment; filename=property-{id}-scenes.ics
```

## Frontend UI (neu)

### Kalender Export Button
- `frontend/src/features/scenes/SceneExportButton.jsx`
- Export-Button in SceneEditor
- "Als Kalender exportieren" Option

### Kalender Abonnement
- `frontend/src/features/scenes/CalendarSubscription.jsx`
- "Kalender abonnieren" Button
- iCal Subscribe Link

## Integration
- `SceneEditor.jsx`: Export Button hinzufügen
- `PropertyManagementPage.jsx`: Kalender Abonnement Tab

## Priorität: LOW (Gast-Experience Erweiterung)
