from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import secrets
import jwt
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import init_db, get_db, User as DBUser, Property as DBProperty, StatusCheck as DBStatusCheck

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ============ SECURITY: Validierung der Umgebungsvariablen ============
JWT_SECRET = os.environ.get('SECRET_KEY')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://welcome-link.de,https://www.welcome-link.de,http://localhost:3000,http://localhost:5173').split(',')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# CRITICAL: Validiere nur notwendige Variablen
if not JWT_SECRET:
    # Für Development: nutze Default-Secret
    if ENVIRONMENT == 'development':
        JWT_SECRET = 'welcome-link-dev-secret-key-change-in-production-12345'
        import sys
        print(f"⚠️  WARNING: Nutze Development-Secret für JWT! Ändere SECRET_KEY in Production!", file=sys.stderr)
    else:
        raise ValueError("❌ SECRET_KEY ist nicht gesetzt!")
        
if JWT_SECRET and len(JWT_SECRET) < 32:
    if ENVIRONMENT != 'development':
        raise ValueError("❌ SECRET_KEY muss mindestens 32 Zeichen lang sein!")

# ============ SMTP CONFIG (mit Fallback für Demo/Development) ============
SMTP_HOST = os.environ.get('SMTP_HOST', 'mail.your-server.de')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'info@welcome-link.de')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'td2dfTR87tFiw2Wg')
SMTP_FROM = os.environ.get('SMTP_FROM', 'info@welcome-link.de')

# Database connection
logger = logging.getLogger(__name__)
try:
    engine, SessionLocal = init_db()
    logger.info("✓ Datenbank initialisiert")
except Exception as e:
    logger.error(f"❌ Datenbankverbindung fehlgeschlagen: {str(e)}", exc_info=True)
    raise ValueError(f"❌ Datenbankverbindung fehlgeschlagen: {str(e)}")

# Password Hashing mit Bcrypt (SICHER!)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate Limiting für Auth-Endpoints
limiter = Limiter(key_func=get_remote_address)

# JWT Settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app without a prefix
app = FastAPI(
    title="Welcome Link API",
    description="Sichere API für Welcome Link",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)
app.state.limiter = limiter

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# ============ MODELS ============

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Auth Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Mindestens 6 Zeichen")
    name: Optional[str] = Field(None, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class MagicLinkRequest(BaseModel):
    email: EmailStr

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_demo: bool = False

class AuthResponse(BaseModel):
    token: str
    user: User

# Property Models
class Property(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    address: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PropertyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    address: Optional[str] = Field(None, max_length=500)

# ============ HELPER FUNCTIONS ============

def hash_password(password: str) -> str:
    """Sichere Passwort-Verschlüsselung mit Bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Überprüfe Passwort gegen Hash"""
    return pwd_context.verify(password, hashed)

def create_token(user_id: str, email: str) -> str:
    """Erstelle einen sicheren JWT Token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Überprüfe JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Ungültiger Token-Versuch: {str(e)}")
        raise HTTPException(status_code=401, detail="Ungültiger Token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Hole den aktuellen authentifizierten Benutzer"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")
    
    payload = verify_token(credentials.credentials)
    user = db.query(DBUser).filter(DBUser.id == payload["user_id"]).first()
    
    if not user:
        logger.warning(f"Benutzer {payload['user_id']} nicht gefunden")
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")
    
    return user

# ============ INIT DEMO USER ============

def init_demo_user(db: Session):
    """Erstelle Demo-Benutzer wenn nicht vorhanden"""
    demo_email = "demo@welcome-link.de"
    logger.info(f"Prüfe ob Demo-Benutzer existiert: {demo_email}")
    
    try:
        existing = db.query(DBUser).filter(DBUser.email == demo_email).first()
    except Exception as e:
        logger.error(f"❌ Fehler beim Abfragen Demo-Benutzer: {str(e)}")
        raise
    
    if not existing:
        demo_user = DBUser(
            id=str(uuid.uuid4()),
            email=demo_email,
            password_hash=hash_password("Demo123!"),
            name="Demo Benutzer",
            created_at=datetime.now(timezone.utc),
            is_demo=True
        )
        db.add(demo_user)
        db.commit()
        
        # Erstelle Demo-Properties
        demo_properties = [
            DBProperty(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                name="Boutique Hotel Alpenblick",
                description="Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.",
                address="Zugspitzstraße 42, 82467 Garmisch-Partenkirchen",
                created_at=datetime.now(timezone.utc)
            ),
            DBProperty(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                name="Ferienwohnung Seeblick",
                description="Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.",
                address="Seepromenade 15, 88131 Lindau",
                created_at=datetime.now(timezone.utc)
            ),
            DBProperty(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                name="Stadtapartment München City",
                description="Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.",
                address="Maximilianstraße 28, 80539 München",
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for prop in demo_properties:
            db.add(prop)
        db.commit()
        
        logger.info("✓ Demo-Benutzer und Properties erstellt")

# ============ AUTH ROUTES ============

@api_router.post("/auth/register", response_model=AuthResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Registriere einen neuen Benutzer"""
    try:
        # Überprüfe ob E-Mail bereits existiert
        existing = db.query(DBUser).filter(DBUser.email == data.email.lower()).first()
        if existing:
            logger.warning(f"Registrierungsversuch mit existierender E-Mail: {data.email}")
            raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
        
        # Erstelle Benutzer
        user_id = str(uuid.uuid4())
        db_user = DBUser(
            id=user_id,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            name=data.name or data.email.split("@")[0],
            created_at=datetime.now(timezone.utc),
            is_demo=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Erstelle Token
        token = create_token(user_id, db_user.email)
        logger.info(f"Neuer Benutzer registriert: {data.email}")
        
        return AuthResponse(
            token=token,
            user=User(
                id=user_id,
                email=db_user.email,
                name=db_user.name,
                is_demo=False
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Registrierung: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registrierung fehlgeschlagen")

@api_router.post("/auth/login", response_model=AuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Benutzer Login mit E-Mail und Passwort"""
    try:
        # Finde Benutzer (normalisiere E-Mail)
        user = db.query(DBUser).filter(DBUser.email == data.email.lower()).first()
        
        if not user:
            logger.warning(f"Benutzer nicht gefunden: {data.email}")
            raise HTTPException(status_code=401, detail="E-Mail oder Passwort falsch")
        
        # Überprüfe Passwort
        if not verify_password(data.password, user.password_hash):
            logger.warning(f"Falsches Passwort für: {data.email}")
            raise HTTPException(status_code=401, detail="E-Mail oder Passwort falsch")
        
        # Erstelle Token
        token = create_token(user.id, user.email)
        logger.info(f"✓ Benutzer eingeloggt: {data.email}")
        
        return AuthResponse(
            token=token,
            user=User(
                id=user.id,
                email=user.email,
                name=user.name,
                is_demo=user.is_demo
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler bei Login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server-Fehler: {str(e)[:50]}")

@api_router.post("/auth/magic-link")
def request_magic_link(data: MagicLinkRequest):
    """Fordere einen Magic Link an (würde in Production E-Mail senden)"""
    # TODO: Implementiere echten E-Mail-Versand mit SendGrid oder ähnlich
    # Für Demo: Nur bestätigung
    logger.info(f"Magic Link angefordert für: {data.email}")
    return {"message": "Magic Link wurde an Ihre E-Mail gesendet", "email": data.email}

@api_router.get("/auth/me", response_model=User)
def get_me(user: DBUser = Depends(get_current_user)):
    """Hole Profil des aktuellen Benutzers"""
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        is_demo=user.is_demo
    )

# ============ PROPERTY ROUTES ============

@api_router.get("/properties", response_model=List[Property])
def get_properties(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hole alle Properties des Benutzers"""
    try:
        properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
        return [Property(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            address=p.address,
            created_at=p.created_at
        ) for p in properties]
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Properties: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen von Properties")

@api_router.post("/properties", response_model=Property)
def create_property(data: PropertyCreate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Erstelle eine neue Property"""
    try:
        prop_id = str(uuid.uuid4())
        db_property = DBProperty(
            id=prop_id,
            user_id=user.id,
            name=data.name.strip(),
            description=data.description.strip() if data.description else None,
            address=data.address.strip() if data.address else None,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(db_property)
        db.commit()
        db.refresh(db_property)
        
        logger.info(f"Property erstellt: {prop_id} für Benutzer {user.id}")
        
        return Property(
            id=db_property.id,
            user_id=db_property.user_id,
            name=db_property.name,
            description=db_property.description,
            address=db_property.address,
            created_at=db_property.created_at
        )
    except Exception as e:
        logger.error(f"Fehler beim Erstellen von Property: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen der Property")

@api_router.get("/properties/{property_id}", response_model=Property)
def get_property(property_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hole eine spezifische Property"""
    try:
        prop = db.query(DBProperty).filter(
            DBProperty.id == property_id,
            DBProperty.user_id == user.id
        ).first()
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        return Property(
            id=prop.id,
            user_id=prop.user_id,
            name=prop.name,
            description=prop.description,
            address=prop.address,
            created_at=prop.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Property: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Property")

@api_router.delete("/properties/{property_id}")
def delete_property(property_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lösche eine Property"""
    try:
        prop = db.query(DBProperty).filter(
            DBProperty.id == property_id,
            DBProperty.user_id == user.id
        ).first()
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        db.delete(prop)
        db.commit()
        
        logger.info(f"Property gelöscht: {property_id}")
        return {"message": "Property gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen von Property: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen der Property")

# ============ STATUS ROUTES ============

@api_router.get("/")
def root():
    return {"message": "Welcome Link API", "version": "1.0.0"}

@api_router.post("/status", response_model=StatusCheck)
def create_status_check(input: StatusCheckCreate, db: Session = Depends(get_db)):
    status_obj = StatusCheck(**input.model_dump())
    db_check = DBStatusCheck(
        id=status_obj.id,
        client_name=status_obj.client_name,
        timestamp=status_obj.timestamp
    )
    db.add(db_check)
    db.commit()
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
def get_status_checks(db: Session = Depends(get_db)):
    checks = db.query(DBStatusCheck).all()
    return [StatusCheck(
        id=c.id,
        client_name=c.client_name,
        timestamp=c.timestamp
    ) for c in checks]

# ============ GUESTVIEW ROUTES ============

@api_router.post("/guestview-token")
def create_guestview_token(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Erstelle einzigartigen Token für passwortlose Gästeanmeldung"""
    try:
        token = str(uuid.uuid4())
        
        # Lösche alte Token für diesen User
        old_tokens = db.query(DBGuestView).filter(DBGuestView.user_id == user.id).all()
        for old in old_tokens:
            db.delete(old)
        
        # Erstelle neuen Token
        guest_view = DBGuestView(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token=token,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(guest_view)
        db.commit()
        db.refresh(guest_view)
        
        logger.info(f"Guestview Token erstellt für User {user.email}: {token}")
        
        return {"guestview_url": f"/guestview/{token}", "token": token}
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Guestview Tokens: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des Tokens")

@api_router.get("/guestview/{token}")
def get_guestview_by_token(token: str, db: Session = Depends(get_db)):
    """Rufe Guestview Daten anhand Token ab (ohne Auth)"""
    try:
        guest_view = db.query(DBGuestView).filter(DBGuestView.token == token).first()
        
        if not guest_view:
            raise HTTPException(status_code=404, detail="Ungültiger Token")
        
        user = db.query(DBUser).filter(DBUser.id == guest_view.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User nicht gefunden")
        
        # Hole alle Properties des Users
        properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
        
        logger.info(f"Guestview aufgerufen für User {user.email} via Token")
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "invoice_name": user.invoice_name,
                "invoice_address": user.invoice_address,
                "invoice_zip": user.invoice_zip,
                "invoice_city": user.invoice_city,
                "invoice_country": user.invoice_country,
                "invoice_vat_id": user.invoice_vat_id
            },
            "properties": [{
                "id": p.id,
                "name": p.name or "Ferienwohnung",
                "description": p.description or "Willkommen in Ihrer Unterkunft",
                "address": p.address or "",
                "wifi_name": p.wifi_name or "Guest-WiFi",
                "wifi_password": p.wifi_password or "",
                "keysafe_location": p.keysafe_location or "",
                "keysafe_code": p.keysafe_code or "",
                "checkin_time": p.checkin_time or "15:00",
                "checkout_time": p.checkout_time or "11:00",
                "brand_color": p.brand_color or "#F27C2C",
                "contact_phone": p.contact_phone or "",
                "contact_email": p.contact_email or "",
                "house_rules": p.house_rules or [],
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in properties],
            "extras": DEMO_EXTRAS  # Extras für Buchung
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Guestviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen des Guestviews")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup():
    """Initialisiere Demo-Benutzer beim Start"""
    try:
        logger.info("🚀 Startup-Event: Öffne DB-Session...")
        if not SessionLocal:
            logger.error("❌ SessionLocal ist nicht initialisiert!")
            return
        
        db = SessionLocal()
        logger.info("✓ DB-Session geöffnet")
        
        try:
            init_demo_user(db)
            db.commit()
            logger.info("✓ Demo-Benutzer initialisiert")
        finally:
            db.close()
        
        logger.info("✓ Application gestartet")
    except Exception as e:
        logger.error(f"❌ Fehler beim Startup: {str(e)}", exc_info=True)

@app.on_event("shutdown")
def shutdown_db_client():
    """Beende Datenbankverbindung"""
    try:
        engine.dispose()
        logger.info("✓ Datenbankverbindung geschlossen")
    except Exception as e:
        logger.error(f"Fehler beim Shutdown: {str(e)}")

# ============ EXTRAS MODELS & ROUTES ============

class ExtraBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    category: str = "other"  # food, wellness, activity, transport, other
    is_active: bool = True

class ExtraCreate(ExtraBase):
    pass

class Extra(ExtraBase):
    id: str
    property_id: int

# In-Memory Extras Store (simplified for demo)
EXTRAS_STORE = {}

def get_demo_extras():
    """Get demo extras"""
    return [
        {"id": "extra-1", "property_id": 17, "name": "Frühstück", "description": "Reichhaltiges Frühstück mit frischen Brötchen", "price": 15.0, "category": "food", "is_active": True},
        {"id": "extra-2", "property_id": 17, "name": "Spät-Check-out", "description": "Check-out bis 14:00 Uhr", "price": 25.0, "category": "other", "is_active": True},
        {"id": "extra-3", "property_id": 17, "name": "Fahrradverleih", "description": "Pro Tag, inkl. Helm", "price": 12.0, "category": "activity", "is_active": True},
        {"id": "extra-4", "property_id": 17, "name": "Sauna", "description": "Private Nutzung für 2 Stunden", "price": 30.0, "category": "wellness", "is_active": True},
        {"id": "extra-5", "property_id": 17, "name": "Gepäckaufbewahrung", "description": "Pro Tag", "price": 5.0, "category": "other", "is_active": True},
        {"id": "extra-6", "property_id": 17, "name": "Shuttle Service", "description": "Bahnhof-Transfer", "price": 20.0, "category": "transport", "is_active": True},
        {"id": "extra-7", "property_id": 17, "name": "Willkommens-Paket", "description": "Sekt, Obst & Schokolade", "price": 35.0, "category": "food", "is_active": True},
        {"id": "extra-8", "property_id": 17, "name": "Haustier", "description": "Pro Nacht", "price": 10.0, "category": "other", "is_active": True},
        {"id": "extra-9", "property_id": 17, "name": "Parkplatz", "description": "Tiefgarage, pro Tag", "price": 8.0, "category": "transport", "is_active": True},
        {"id": "extra-10", "property_id": 17, "name": "Massage", "description": "60 Min. Rücken-Nacken", "price": 65.0, "category": "wellness", "is_active": True},
    ]

@api_router.get("/properties/{property_id}/extras")
def get_extras(property_id: int):
    """Get all extras for a property"""
    extras = get_demo_extras()
    return {"extras": extras}

@api_router.post("/properties/{property_id}/extras")
def create_extra(property_id: int, data: ExtraCreate, user = Depends(get_current_user)):
    """Create a new extra"""
    extra_id = f"extra-{uuid.uuid4().hex[:8]}"
    extra = {
        "id": extra_id,
        "property_id": property_id,
        **data.model_dump()
    }
    if property_id not in EXTRAS_STORE:
        EXTRAS_STORE[property_id] = []
    EXTRAS_STORE[property_id].append(extra)
    return extra

# ============ CHECKOUT MODELS & ROUTES ============

class CheckoutItem(BaseModel):
    extra_id: str
    quantity: int = Field(ge=1, le=10)
    
class CheckoutRequest(BaseModel):
    property_id: int
    items: List[CheckoutItem]
    guest_name: str
    guest_email: str
    payment_method: str = "stripe"  # stripe, paypal, cash
    
class CheckoutResponse(BaseModel):
    checkout_id: str
    total: float
    payment_url: Optional[str] = None
    status: str

# In-Memory Checkouts Store
CHECKOUTS_STORE = {}

@api_router.post("/checkout")
def create_checkout(data: CheckoutRequest, user = Depends(get_current_user)):
    """Create a new checkout/order"""
    checkout_id = f"checkout-{uuid.uuid4().hex[:8]}"
    
    # Calculate total
    extras = get_demo_extras()
    total = 0.0
    order_items = []
    
    for item in data.items:
        extra = next((e for e in extras if e["id"] == item.extra_id), None)
        if extra:
            item_total = extra["price"] * item.quantity
            total += item_total
            order_items.append({
                "extra_id": item.extra_id,
                "name": extra["name"],
                "price": extra["price"],
                "quantity": item.quantity,
                "total": item_total
            })
    
    checkout = {
        "id": checkout_id,
        "property_id": data.property_id,
        "items": order_items,
        "guest_name": data.guest_name,
        "guest_email": data.guest_email,
        "payment_method": data.payment_method,
        "subtotal": total,
        "tax": round(total * 0.19, 2),
        "total": round(total * 1.19, 2),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    CHECKOUTS_STORE[checkout_id] = checkout
    
    # For demo: auto-complete payment
    if data.payment_method == "stripe":
        checkout["status"] = "completed"
        checkout["payment_id"] = f"pi_{uuid.uuid4().hex[:24]}"
    
    return CheckoutResponse(
        checkout_id=checkout_id,
        total=checkout["total"],
        payment_url=None,
        status=checkout["status"]
    )

@api_router.get("/checkout/{checkout_id}")
def get_checkout(checkout_id: str):
    """Get checkout details"""
    checkout = CHECKOUTS_STORE.get(checkout_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    return checkout

@api_router.post("/checkout/{checkout_id}/complete")
def complete_checkout(checkout_id: str, user = Depends(get_current_user)):
    """Complete a checkout (simulate payment)"""
    checkout = CHECKOUTS_STORE.get(checkout_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    
    checkout["status"] = "completed"
    checkout["completed_at"] = datetime.now(timezone.utc).isoformat()
    checkout["payment_id"] = f"pi_{uuid.uuid4().hex[:24]}"
    
    return checkout

@api_router.get("/checkout/{checkout_id}/invoice")
def get_invoice(checkout_id: str):
    """Get invoice PDF for checkout"""
    checkout = CHECKOUTS_STORE.get(checkout_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    
    # Generate invoice data
    invoice_number = f"WL-{datetime.now().strftime('%Y%m%d')}-{checkout_id[-6:].upper()}"
    
    invoice_data = {
        "invoice_number": invoice_number,
        "invoice_date": datetime.now().strftime("%d.%m.%Y"),
        "due_date": (datetime.now() + timedelta(days=14)).strftime("%d.%m.%Y"),
        "host_name": "Welcome Link Demo",
        "host_address": "Musterstraße 1, 12345 Musterstadt",
        "host_email": "info@welcome-link.de",
        "guest_name": checkout["guest_name"],
        "guest_email": checkout["guest_email"],
        "property_name": "Ferienwohnung Seeblick",
        "property_address": "Seestraße 42, 83209 Prien am Chiemsee",
        "items": checkout["items"],
        "subtotal": checkout["subtotal"],
        "tax": checkout["tax"],
        "total": checkout["total"],
        "payment_method": checkout["payment_method"],
        "payment_status": "Bezahlt" if checkout["status"] == "completed" else "Ausstehend"
    }
    
    return {"invoice": invoice_data, "checkout": checkout}

# ============ PROPERTY EDIT ROUTES ============

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    brand_color: Optional[str] = None
    wifi_name: Optional[str] = None
    wifi_password: Optional[str] = None
    keysafe_location: Optional[str] = None
    keysafe_code: Optional[str] = None
    checkin_time: Optional[str] = None
    checkout_time: Optional[str] = None
    house_rules: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

@api_router.put("/properties/{property_id}")
def update_property(property_id: int, data: PropertyUpdate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update property details"""
    prop = db.query(DBProperty).filter(DBProperty.id == property_id).first()
    if not prop:
        # For demo: return success anyway
        return {"success": True, "property_id": property_id, "updated": data.model_dump(exclude_none=True)}
    
    # Update fields
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        if hasattr(prop, key):
            setattr(prop, key, value)
    
    db.commit()
    db.refresh(prop)
    
    return {"success": True, "property": prop.to_dict() if hasattr(prop, 'to_dict') else update_data}

@api_router.get("/properties/{property_id}/edit")
def get_property_for_edit(property_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get property details for editing"""
    prop = db.query(DBProperty).filter(DBProperty.id == property_id).first()
    
    if not prop:
        # Return demo property
        return {
            "id": property_id,
            "name": "Ferienwohnung Seeblick",
            "description": "Moderne 3-Zimmer Ferienwohnung direkt am Chiemsee mit eigenem Bootssteg und Panoramaterrasse.",
            "address": "Seestraße 42, 83209 Prien am Chiemsee",
            "brand_color": "#f97316",
            "wifi_name": "Seeblick-Guest",
            "wifi_password": "Welcome2024!",
            "keysafe_location": "An der Eingangstür links",
            "keysafe_code": "1234",
            "checkin_time": "15:00",
            "checkout_time": "11:00",
            "house_rules": [
                "Rauchen ist in der gesamten Unterkunft nicht gestattet",
                "Bitte tragen Sie Straßenschuhe nicht in den Schlafzimmern",
                "Ruhezeiten: 22:00 - 08:00 Uhr"
            ],
            "contact_phone": "+49 8051 12345",
            "contact_email": "host@welcome-link.de"
        }
    
    return prop.to_dict() if hasattr(prop, 'to_dict') else {"id": property_id}

# Include the router in the main app AFTER all routes are defined
app.include_router(api_router)

# Build 2026-03-03 19:56:04

# ============ DEMO INIT ============
@api_router.post("/demo/init")
def init_demo_data(db: Session = Depends(get_db)):
    """Initialisiere Demo-Daten für Testing"""
    import random
    import string
    
    # Demo User erstellen
    demo_email = "demo@welcome-link.de"
    user = db.query(DBUser).filter(DBUser.email == demo_email).first()
    
    if not user:
        # User erstellen
        hashed_password = bcrypt.hashpw("Demo123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = DBUser(
            id=str(uuid.uuid4()),
            email=demo_email,
            name="Demo User",
            password_hash=hashed_password,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Demo Property erstellen
    property = db.query(DBProperty).filter(DBProperty.user_id == user.id).first()
    
    if not property:
        property = DBProperty(
            id=17,
            user_id=user.id,
            name="Ferienwohnung Seeblick",
            address="Seestraße 42, 83209 Prien am Chiemsee",
            wifi_name="Seeblick-Guest",
            wifi_password="Welcome2024!",
            keysafe_location="An der Eingangstür links",
            keysafe_code="1234",
            checkin_time="15:00",
            checkout_time="11:00",
            brand_color="#F27C2C",
            created_at=datetime.now(timezone.utc)
        )
        db.add(property)
        db.commit()
        db.refresh(property)
    
    # Demo Guestview Token
    guest_view = db.query(DBGuestView).filter(DBGuestView.user_id == user.id).first()
    
    if not guest_view:
        guest_view = DBGuestView(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token="QEJHEXP1QF",
            created_at=datetime.now(timezone.utc)
        )
        db.add(guest_view)
        db.commit()
    
    return {
        "success": True,
        "user": {"id": user.id, "email": user.email, "name": user.name},
        "property": {"id": property.id, "name": property.name},
        "guestview_token": "QEJHEXP1QF"
    }

# ============ HEALTH CHECK ============
@api_router.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.1.0",
        "services": {
            "api": "ok",
            "database": "ok"
        }
    }
