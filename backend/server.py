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
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# CRITICAL: Validiere nur notwendige Variablen
if not JWT_SECRET:
    raise ValueError("❌ SECRET_KEY ist nicht gesetzt!")
if JWT_SECRET and len(JWT_SECRET) < 32:
    raise ValueError("❌ SECRET_KEY muss mindestens 32 Zeichen lang sein!")

# Database connection
try:
    engine, SessionLocal = init_db()
    logger = logging.getLogger(__name__)
    logger.info("✓ Datenbank initialisiert")
except Exception as e:
    raise ValueError(f"❌ Datenbankverbindung fehlgeschlagen: {str(e)}")

# Password Hashing mit Bcrypt (SICHER!)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate Limiting für Auth-Endpoints
limiter = Limiter(key_func=get_remote_address)

# JWT Settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
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
    password: str = Field(min_length=8, description="Mindestens 8 Zeichen")
    name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Überprüfe Passwort-Stärke"""
        if not any(char.isupper() for char in v):
            raise ValueError("Passwort muss mindestens einen Großbuchstaben enthalten")
        if not any(char.isdigit() for char in v):
            raise ValueError("Passwort muss mindestens eine Zahl enthalten")
        return v

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
    existing = db.query(DBUser).filter(DBUser.email == demo_email).first()
    
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
        
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning(f"Fehlgeschlagener Login-Versuch: {data.email}")
            # Gebe keine Details preis
            raise HTTPException(status_code=401, detail="E-Mail oder Passwort falsch")
        
        # Erstelle Token
        token = create_token(user.id, user.email)
        logger.info(f"Benutzer eingeloggt: {data.email}")
        
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
        logger.error(f"Fehler bei Login: {str(e)}")
        raise HTTPException(status_code=500, detail="Login fehlgeschlagen")

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

# Include the router in the main app
app.include_router(api_router)

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
        db = SessionLocal()
        init_demo_user(db)
        db.close()
        logger.info("✓ Application gestartet, Demo-Benutzer initialisiert")
    except Exception as e:
        logger.error(f"Fehler beim Startup: {str(e)}")

@app.on_event("shutdown")
def shutdown_db_client():
    """Beende Datenbankverbindung"""
    try:
        engine.dispose()
        logger.info("✓ Datenbankverbindung geschlossen")
    except Exception as e:
        logger.error(f"Fehler beim Shutdown: {str(e)}")
