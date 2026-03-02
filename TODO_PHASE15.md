# Phase 15: Key-Safe Info UI - TODO

## Features
- [ ] Key-Safe Informationen in Property anzeigen
- [ ] Key-Safe Koordinaten anzeigen
- [ ] Anleitung zur Key-Safe Bedienung

## Backend API Endpoints (neu)

### Key-Safe Info
```
GET    /api/properties/{id}/keysafe
PUT    /api/properties/{id}/keysafe
```

### Key-Safe Model Erweiterung
```python
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    # Key-Safe Info
    keysafe_location = Column(String(500))
    keysafe_code = Column(String(50))
    keysafe_instructions = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## Frontend UI (neu)

### Key-Safe Info Card
- `frontend/src/features/property/KeySafeInfoCard.jsx`
- Key-Safe Standort anzeigen
- Code anzeigen (mit Toggle für Sichtbarkeit)
- Anleitung anzeigen
- Edit Button

### Property Management Page
- Tab "Key-Safe" hinzufügen
- KeySafeInfoCard integrieren
- Edit Modal für Key-Safe Daten

## Integration
- `PropertyManagementPage.jsx`: Neuer Tab für Key-Safe

## Priorität: MEDIUM (Gäste erwarten Key-Safe Info)
