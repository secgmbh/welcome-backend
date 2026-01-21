from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ============ SECURITY: Validierung der Umgebungsvariablen ============
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'welcome_link')
JWT_SECRET = os.environ.get('SECRET_KEY')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# CRITICAL: Validiere nur notwendige Variablen
if not JWT_SECRET:
    raise ValueError("❌ SECRET_KEY ist nicht gesetzt!")
if JWT_SECRET and len(JWT_SECRET) < 32:
    raise ValueError("❌ SECRET_KEY muss mindestens 32 Zeichen lang sein!")

# MongoDB connection (optional)
client = None
db = None
if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Hole den aktuellen authentifizierten Benutzer"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")
    
    payload = verify_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    
    if not user:
        logger.warning(f"Benutzer {payload['user_id']} nicht gefunden")
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")
    
    return user

# ============ INIT DEMO USER ============

async def init_demo_user():
    """Erstelle Demo-Benutzer wenn nicht vorhanden"""
    demo_email = "demo@welcome-link.de"
    existing = await db.users.find_one({"email": demo_email})
    
    if not existing:
        demo_user = {
            "id": str(uuid.uuid4()),
            "email": demo_email,
            "password_hash": hash_password("Demo123!"),  # Stark Passwort mit Validator
            "name": "Demo Benutzer",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_demo": True
        }
        await db.users.insert_one(demo_user)
        
        # Erstelle Demo-Properties
        demo_properties = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user["id"],
                "name": "Boutique Hotel Alpenblick",
                "description": "Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.",
                "address": "Zugspitzstraße 42, 82467 Garmisch-Partenkirchen",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user["id"],
                "name": "Ferienwohnung Seeblick",
                "description": "Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.",
                "address": "Seepromenade 15, 88131 Lindau",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user["id"],
                "name": "Stadtapartment München City",
                "description": "Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.",
                "address": "Maximilianstraße 28, 80539 München",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for prop in demo_properties:
            await db.properties.insert_one(prop)
        
        logger.info("✓ Demo-Benutzer und Properties erstellt")

# ============ AUTH ROUTES ============

@api_router.post("/auth/register", response_model=AuthResponse)
async def register(data: UserRegister):
    """Registriere einen neuen Benutzer"""
    try:
        # Überprüfe ob E-Mail bereits existiert
        existing = await db.users.find_one({"email": data.email.lower()})
        if existing:
            logger.warning(f"Registrierungsversuch mit existierender E-Mail: {data.email}")
            raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
        
        # Erstelle Benutzer
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": data.email.lower(),
            "password_hash": hash_password(data.password),
            "name": data.name or data.email.split("@")[0],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_demo": False
        }
        
        await db.users.insert_one(user_doc)
        
        # Erstelle Token
        token = create_token(user_id, user_doc["email"])
        logger.info(f"Neuer Benutzer registriert: {data.email}")
        
        return AuthResponse(
            token=token,
            user=User(
                id=user_id,
                email=user_doc["email"],
                name=user_doc["name"],
                is_demo=False
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Registrierung: {str(e)}")
        raise HTTPException(status_code=500, detail="Registrierung fehlgeschlagen")

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(data: UserLogin):
    """Benutzer Login mit E-Mail und Passwort"""
    try:
        # Finde Benutzer (normalisiere E-Mail)
        user = await db.users.find_one({"email": data.email.lower()})
        
        if not user or not verify_password(data.password, user.get("password_hash", "")):
            logger.warning(f"Fehlgeschlagener Login-Versuch: {data.email}")
            # Gebe keine Details preis
            raise HTTPException(status_code=401, detail="E-Mail oder Passwort falsch")
        
        # Erstelle Token
        token = create_token(user["id"], user["email"])
        logger.info(f"Benutzer eingeloggt: {data.email}")
        
        return AuthResponse(
            token=token,
            user=User(
                id=user["id"],
                email=user["email"],
                name=user.get("name"),
                is_demo=user.get("is_demo", False)
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Login: {str(e)}")
        raise HTTPException(status_code=500, detail="Login fehlgeschlagen")

@api_router.post("/auth/magic-link")
async def request_magic_link(data: MagicLinkRequest):
    """Fordere einen Magic Link an (würde in Production E-Mail senden)"""
    # TODO: Implementiere echten E-Mail-Versand mit SendGrid oder ähnlich
    # Für Demo: Nur bestätigung
    logger.info(f"Magic Link angefordert für: {data.email}")
    return {"message": "Magic Link wurde an Ihre E-Mail gesendet", "email": data.email}

@api_router.get("/auth/me", response_model=User)
async def get_me(user: dict = Depends(get_current_user)):
    """Hole Profil des aktuellen Benutzers"""
    return User(**user)

# ============ PROPERTY ROUTES ============

@api_router.get("/properties", response_model=List[Property])
async def get_properties(user: dict = Depends(get_current_user)):
    """Hole alle Properties des Benutzers"""
    try:
        properties = await db.properties.find(
            {"user_id": user["id"]}, 
            {"_id": 0}
        ).to_list(1000)
        
        return properties
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Properties: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen von Properties")

@api_router.post("/properties", response_model=Property)
async def create_property(data: PropertyCreate, user: dict = Depends(get_current_user)):
    """Erstelle eine neue Property"""
    try:
        prop_id = str(uuid.uuid4())
        prop_doc = {
            "id": prop_id,
            "user_id": user["id"],
            "name": data.name.strip(),
            "description": data.description.strip() if data.description else None,
            "address": data.address.strip() if data.address else None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.properties.insert_one(prop_doc)
        logger.info(f"Property erstellt: {prop_id} für Benutzer {user['id']}")
        
        return Property(**prop_doc)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen von Property: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen der Property")

@api_router.get("/properties/{property_id}", response_model=Property)
async def get_property(property_id: str, user: dict = Depends(get_current_user)):
    """Hole eine spezifische Property"""
    try:
        prop = await db.properties.find_one(
            {"id": property_id, "user_id": user["id"]},
            {"_id": 0}
        )
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        return Property(**prop)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Property: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Property")

@api_router.delete("/properties/{property_id}")
async def delete_property(property_id: str, user: dict = Depends(get_current_user)):
    """Lösche eine Property"""
    try:
        result = await db.properties.delete_one({"id": property_id, "user_id": user["id"]})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        logger.info(f"Property gelöscht: {property_id}")
        return {"message": "Property gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen von Property: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen der Property")

# ============ STATUS ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "Welcome Link API", "version": "1.0.0"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

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
async def startup():
    """Initialisiere Demo-Benutzer beim Start"""
    try:
        await init_demo_user()
        logger.info("✓ Application gestartet, Demo-Benutzer initialisiert")
    except Exception as e:
        logger.error(f"Fehler beim Startup: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Beende MongoDB-Verbindung"""
    try:
        client.close()
        logger.info("✓ Datenbankverbindung geschlossen")
    except Exception as e:
        logger.error(f"Fehler beim Shutdown: {str(e)}")
