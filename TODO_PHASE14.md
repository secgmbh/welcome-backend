# Phase 14: Branding & AI Enhancement - TODO

## Features
- [ ] Branding-Engine (brandColor dynamisch anpassen)
- [ ] AI Copywriter (automatische Generierung von Texten)
- [ ] KI-Inhalts-Generator für Szenen

## Backend API Endpoints (neu)

### Branding-Engine
```
GET    /api/branding                    # Branding-Konfiguration holen
POST   /api/branding                    # Branding aktualisieren
```

### Branding Model Erweiterung
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(200))
    email = Column(String(200), unique=True, index=True)
    password = Column(String(255))
    is_email_verified = Column(Boolean, default=False)
    role = Column(String(50), default='host')  # host, cleaner, admin
    brand_color = Column(String(7), default='#F27C2C')  # Hex Farbe
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

### AI Copywriter API
```
POST   /api/ai/copywriter               # AI Text generieren
```

### AI Copywriter Request/Response
```python
class AICopyRequest(BaseModel):
    prompt: str
    language: Optional[str] = "de"

class AICopyResponse(BaseModel):
    text: str
    model: str
    tokens_used: int
```

## Frontend UI (neu)

### Branding Editor
- `frontend/src/features/settings/BrandingEditor.jsx`
- Farbauswahl für brandColor
- Logo Upload
- Vorschau der Anpassung

### AI Copywriter
- `frontend/src/features/ai/AICopywriter.jsx`
- Prompt Eingabe
- Sprachauswahl (DE/EN)
- Generierte Texte anzeigen
- Copy-to-Clipboard

## Integration
- `SettingsPage.jsx`: Branding Tab hinzufügen
- `SceneEditor.jsx`: AI Copywriter Button integrieren

## Priorität: HIGH (MVP-Finisher)
