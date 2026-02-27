# Phase 12: Cleaner & Admin Features - TODO

## Features
- [ ] Cleaner Login (passwortlose cleanerId URL)
- [ ] Echtzeit-Taskliste (Reinigungsaufgaben)
- [ ] Key-Safe Info (Zugangscodes aus Property-Daten)
- [ ] Kalender-Sync (.ics Export für Google/Outlook)

## Backend API Endpoints (neu)

### Cleaner Login
```
POST   /api/cleaner/login               # Cleaner anmelden
GET    /api/cleaner/profile             # Cleaner Profil holen
```

### Task-Management
```
GET    /api/tasks?property_id={id}      # Aufgaben für Property holen
POST   /api/tasks                       # Neue Aufgabe erstellen
PUT    /api/tasks/{id}                  # Aufgabe aktualisieren
POST   /api/tasks/{id}/complete         # Aufgabe als erledigt markieren
GET    /api/tasks/export/ics            # .ics Export herunterladen
```

### Task Model
```python
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    cleaner_id = Column(String(36), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## Frontend UI (neu)

### Cleaner Dashboard
- `frontend/src/features/cleaner/CleanerDashboard.jsx`
- Task-Liste mit Filtern
- Task-Status aktualisieren
- Kalender-Export Button

### Key-Safe Info
- `frontend/src/features/property/KeySafeInfo.jsx`
- Zugangscodes anzeigen (versteckt bis Required)
- Sicherheits-Hinweise

## Integration
- `PropertyManagementPage.jsx`: Tabs für Tasks & Key-Safe
- `GuestviewPage.jsx`: Cleaner-Login-Option hinzufügen
