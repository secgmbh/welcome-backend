# Phase 9: Partner-Modul & Smart Rules - TODO

## Backend API Endpoints (neu)

### Partner-Modul
```
GET    /api/partners                    # Liste aller Partner für den User
POST   /api/partners                    # Neuen Partner erstellen
PUT    /api/partners/{id}               # Partner aktualisieren
DELETE /api/partners/{id}               # Partner löschen
```

### Partner Model
```python
class Partner(Base):
    __tablename__ = "partners"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # taxi, spa, restaurant, etc.
    address = Column(String(500))
    phone = Column(String(50))
    email = Column(String(200))
    website = Column(String(500))
    image_url = Column(String(500))
    commission_rate = Column(Float, default=0)  # Provisions-Link
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

### Smart Rules
```
GET    /api/smart-rules                 # Liste aller Smart Rules
POST   /api/smart-rules                 # Neue Smart Rule erstellen
PUT    /api/smart-rules/{id}            # Smart Rule aktualisieren
DELETE /api/smart-rules/{id}            # Smart Rule löschen
```

### Smart Rule Model
```python
class SmartRule(Base):
    __tablename__ = "smart_rules"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50))  # time_based, guest_action, etc.
    condition = Column(Text)  # JSON für Bedingungen
    action = Column(Text)  # JSON für Aktionen
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## Frontend UI (neu)

### Partner-Manager
- `frontend/src/features/partners/PartnerManager.jsx`
- Liste aller Partner mit Kategorien
- CRUD-Operationen (Create, Read, Update, Delete)
- Provisions-Links konfigurieren

### Smart Rules Editor
- `frontend/src/features/smartrules/SmartRulesEditor.jsx`
- Regel erstellen/bearbeiten
- Trigger-Typen: Zeitgesteuert, Guest Action
- Bedingungen konfigurieren
- Aktionen definieren

## Integration
- `PropertyManagementPage.jsx`: Tabs für Partner & Smart Rules hinzufügen
