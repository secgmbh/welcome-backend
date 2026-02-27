from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
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
from database import init_db, get_db, User as DBUser, Property as DBProperty, StatusCheck as DBStatusCheck, GuestView as DBGuestView, Scene as DBScene, Extra as DBExtra, Bundle as DBBundle, BundleExtra as DBBundleExtra, ABTest as DBABTest, Partner as DBPartner, SmartRule as DBSmartRule, Scene as DBScene, Extra as DBExtra, ABTest as DBABTest, Partner as DBPartner, SmartRule as DBSmartRule

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

# Warnung wenn Leeres Password (nur in Development)
if not SMTP_PASSWORD and ENVIRONMENT == 'development':
    import sys
    print(f"⚠️  WARNING: SMTP_PASSWORD ist leer! E-Mails funktionieren nicht.", file=sys.stderr)

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
            is_demo=True,
            # Dummy Rechnungsdaten
            invoice_name="Alpenblick Hospitality GmbH",
            invoice_address="Bergstraße 12",
            invoice_zip="82467",
            invoice_city="Garmisch-Partenkirchen",
            invoice_country="Deutschland",
            invoice_vat_id="DE123456789"
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
        
        # Erstelle festen GuestView-Token für Demo
        demo_guestview_token = "demo-guest-view-token"
        guest_view = DBGuestView(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            token=demo_guestview_token,
            created_at=datetime.now(timezone.utc)
        )
        db.add(guest_view)
        
        db.commit()
        logger.info(f"✓ Demo-Benutzer, Properties und GuestView-Token erstellt: /guestview/{demo_guestview_token}")

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


# ============ EMAIL VERIFICATION ROUTES ============

@api_router.post("/auth/verify-email")
def verify_email(data: dict, db: Session = Depends(get_db)):
    """Verifiziere E-Mail mit Token"""
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token fehlt")
    
    try:
        user = db.query(DBUser).filter(DBUser.email_verification_token == token).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Ungültiger Token")
        
        # Prüfe ob Token abgelaufen ist
        if user.email_verification_token_expires and datetime.now(timezone.utc) > user.email_verification_token_expires:
            raise HTTPException(status_code=400, detail="Token ist abgelaufen")
        
        # Verifiziere E-Mail
        user.is_email_verified = True
        user.email_verification_token = None  # Token zurücksetzen
        db.commit()
        
        logger.info(f"✓ E-Mail verifiziert: {user.email}")
        
        return {"message": "E-Mail erfolgreich verifiziert", "email": user.email}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Email-Verifizierung: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Verifizierung fehlgeschlagen")


@api_router.post("/auth/resend-verification")
def resend_verification(data: dict, db: Session = Depends(get_db)):
    """Sende Verifizierungs-E-Mail erneut"""
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="E-Mail fehlt")
    
    try:
        user = db.query(DBUser).filter(DBUser.email == email.lower()).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
        
        # Prüfe ob bereits verifiziert
        if user.is_email_verified:
            raise HTTPException(status_code=400, detail="E-Mail bereits verifiziert")
        
        # Generiere neuen Token
        import secrets
        new_token = secrets.token_urlsafe(32)
        from datetime import timedelta
        user.email_verification_token = new_token
        user.email_verification_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.commit()
        
        logger.info(f"Verifizierungs-E-Mail erneut gesendet an: {email}")
        
        # TODO: In Production echte E-Mail senden
        return {
            "message": "Verifizierungs-E-Mail erneut gesendet",
            "email": email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Resenden der Verifizierung: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Resenden")

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

class PropertyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    address: Optional[str] = Field(None, max_length=500)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    invoice_name: Optional[str] = Field(None, max_length=200)
    invoice_address: Optional[str] = Field(None, max_length=500)
    invoice_zip: Optional[str] = Field(None, max_length=20)
    invoice_city: Optional[str] = Field(None, max_length=100)
    invoice_country: Optional[str] = Field(None, max_length=100)
    invoice_vat_id: Optional[str] = Field(None, max_length=50)

@api_router.put("/properties/{property_id}", response_model=Property)
def update_property(property_id: str, data: PropertyUpdate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aktualisiere eine Property"""
    try:
        prop = db.query(DBProperty).filter(
            DBProperty.id == property_id,
            DBProperty.user_id == user.id
        ).first()
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        if data.name is not None:
            prop.name = data.name.strip()
        if data.description is not None:
            prop.description = data.description.strip()
        if data.address is not None:
            prop.address = data.address.strip()
        
        db.commit()
        db.refresh(prop)
        
        logger.info(f"Property aktualisiert: {property_id}")
        
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
        logger.error(f"Fehler beim Aktualisieren von Property: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren der Property")

@api_router.put("/auth/profile")
def update_profile(data: UserProfileUpdate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aktualisiere Benutzerprofil"""
    try:
        if data.name is not None:
            user.name = data.name.strip()
        if data.invoice_name is not None:
            user.invoice_name = data.invoice_name.strip()
        if data.invoice_address is not None:
            user.invoice_address = data.invoice_address.strip()
        if data.invoice_zip is not None:
            user.invoice_zip = data.invoice_zip.strip()
        if data.invoice_city is not None:
            user.invoice_city = data.invoice_city.strip()
        if data.invoice_country is not None:
            user.invoice_country = data.invoice_country.strip()
        if data.invoice_vat_id is not None:
            user.invoice_vat_id = data.invoice_vat_id.strip()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Profil aktualisiert: {user.email}")
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "invoice_name": user.invoice_name,
            "invoice_address": user.invoice_address,
            "invoice_zip": user.invoice_zip,
            "invoice_city": user.invoice_city,
            "invoice_country": user.invoice_country,
            "invoice_vat_id": user.invoice_vat_id
        }
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Profils: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren des Profils")

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


@api_router.get("/debug-db-schema")
def debug_db_schema(db: Session = Depends(get_db)):
    """Debug Endpoint für DB Schema"""
    try:
        # Prüfe user_id Type
        result = db.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'properties' AND column_name = 'user_id'").fetchone()
        user_id_type = result[0] if result else "N/A"
        
        # Prüfe description Spalte
        result = db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'properties' AND column_name = 'description'").fetchone()
        has_description = result is not None
        
        # Prüfe Tabellen
        result = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'").fetchall()
        tables = [r[0] for r in result]
        
        return {
            "tables": tables,
            "user_id_type": user_id_type,
            "has_description": has_description
        }
    except Exception as e:
        return {"error": str(e)}


@api_router.get("/guestview-public-qr-data")
def get_guestview_public_qr_data(db: Session = Depends(get_db)):
    """Öffentlicher Endpoint für QR Code Daten (ohne Auth) - für Demo"""
    from sqlalchemy import text as sql_text
    try:
        # Hole Demo-User anhand E-Mail
        demo_email = "demo@welcome-link.de"
        user = db.query(DBUser).filter(DBUser.email == demo_email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Demo-User {demo_email} nicht gefunden")
        
        # Hole Properties direkt mit raw SQL (um alle Spalten zu bekommen)
        stmt = sql_text("SELECT id, user_id, name, address, created_at FROM properties WHERE user_id = :user_id")
        sql_result = db.execute(stmt, {"user_id": str(user.id)}).fetchall()
        
        properties = []
        for row in sql_result:
            p = type('Property', (), {})()
            p.id = row.id
            p.user_id = row.user_id
            p.name = row.name
            p.address = row.address
            p.created_at = row.created_at
            p.description = None
            properties.append(p)
        
        result = []
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://www.welcome-link.de')
        qr_url = f"{frontend_url}/guestview/demo-guest-view-token"
        
        for p in properties:
            result.append({
                "id": p.id,
                "user_id": p.user_id,
                "name": p.name,
                "description": p.description,
                "address": p.address,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "qr_code_url": qr_url
            })
        
        logger.info(f"QR Daten zurückgegeben für {len(properties)} Properties von User {user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Fehler beim Abrufen der QR-Daten: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@api_router.post("/demo/init")
def init_demo_user_endpoint(db: Session = Depends(get_db)):
    """Initialisiere Demo User manuell"""
    init_demo_user(db)
    return {"message": "Demo User initialisiert"}


@api_router.get("/guestview-qr-simple")
def get_guestview_qr_data_simple():
    """Simple QR Data Endpoint ohne Datenbank (für Demo)"""
    import json
    import os
    
    try:
        # Versuche verschiedene Pfade für die JSON Datei
        json_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_properties.json"),
            "backend/demo_properties.json",
            "demo_properties.json"
        ]
        
        json_data = None
        for path in json_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    break
            except FileNotFoundError:
                continue
        
        if json_data is None:
            raise HTTPException(status_code=500, detail="demo_properties.json nicht gefunden")
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://www.welcome-link.de')
        qr_url = f"{frontend_url}/guestview/demo-guest-view-token"
        
        result = []
        for p in json_data:
            result.append({
                "id": p.get("id"),
                "user_id": p.get("user_id"),
                "name": p.get("name"),
                "description": p.get("description"),
                "address": p.get("address"),
                "created_at": p.get("created_at"),
                "qr_code_url": qr_url
            })
        
        logger.info(f"QR Daten (simple) zurückgegeben für {len(json_data)} Properties")
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Fehler beim Abrufen der QR-Daten (simple): {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@api_router.get("/demo/init-guestview")
def init_demo_guestview(db: Session = Depends(get_db)):
    """Initialisiere Guestview Token für Demo User"""
    from sqlalchemy import text as sql_text
    try:
        demo_email = "demo@welcome-link.de"
        user = db.query(DBUser).filter(DBUser.email == demo_email.lower()).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Demo-User {demo_email} nicht gefunden")
        
        demo_token = "demo-guest-view-token"
        
        # Prüfe ob Token existiert
        existing = db.query(DBGuestView).filter(DBGuestView.token == demo_token).first()
        
        if existing:
            logger.info(f"✓ Guestview Token existiert bereits: {demo_token}")
            return {"token": demo_token, "url": f"/guestview/{demo_token}"}
        
        # Erstelle Token
        from sqlalchemy import text as sql_text
        stmt = sql_text("INSERT INTO guest_views (id, user_id, token, created_at) VALUES (:id, :user_id, :token, :created_at)")
        db.execute(stmt, {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "token": demo_token,
            "created_at": datetime.now(timezone.utc)
        })
        db.commit()
        
        logger.info(f"✓ Guestview Token erstellt: {demo_token}")
        return {"token": demo_token, "url": f"/guestview/{demo_token}"}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Fehler beim Erstellen des Guestview Tokens: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


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
                "name": p.name,
                "description": p.description,
                "address": p.address,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in properties]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Guestviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen des Guestviews")

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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

# ============== SCENE API ENDPOINTS ==============
class SceneCreate(BaseModel):
    property_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    order: Optional[int] = 0

class SceneResponse(BaseModel):
    id: str
    property_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    order: int
    created_at: str

@api_router.get("/scenes", response_model=List[SceneResponse], dependencies=[Depends(get_current_user)])
def get_scenes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Scenes für den aktuellen User"""
    scenes = db.query(Scene).filter(Scene.property_id.in_(
        db.query(Property.id).filter(Property.user_id == user.id)
    )).order_by(Scene.order).all()
    return scenes

@api_router.post("/scenes", response_model=SceneResponse, dependencies=[Depends(get_current_user)])
def create_scene(scene: SceneCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle eine neue Scene"""
    # Prüfe, ob Property dem User gehört
    property = db.query(Property).filter(
        Property.id == scene.property_id,
        Property.user_id == user.id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property nicht gefunden oder nicht berechtigt")
    
    scene_obj = Scene(
        id=str(uuid.uuid4()),
        property_id=scene.property_id,
        title=scene.title,
        description=scene.description,
        image_url=scene.image_url,
        order=scene.order or 0
    )
    db.add(scene_obj)
    db.commit()
    db.refresh(scene_obj)
    return scene_obj

@api_router.put("/scenes/{scene_id}", response_model=SceneResponse, dependencies=[Depends(get_current_user)])
def update_scene(scene_id: str, scene: SceneCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere eine Scene"""
    db_scene = db.query(Scene).filter(
        Scene.id == scene_id,
        Scene.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    db_scene.title = scene.title
    db_scene.description = scene.description
    db_scene.image_url = scene.image_url
    db_scene.order = scene.order or 0
    db.commit()
    db.refresh(db_scene)
    return db_scene

@api_router.delete("/scenes/{scene_id}", dependencies=[Depends(get_current_user)])
def delete_scene(scene_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche eine Scene"""
    db_scene = db.query(Scene).filter(
        Scene.id == scene_id,
        Scene.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_scene:
        raise HTTPException(status_code=404, detail="Scene nicht gefunden")
    
    db.delete(db_scene)
    db.commit()
    return {"message": "Scene gelöscht"}

# ============== END SCENE API ENDPOINTS ==============

# ============== A/B TESTING API ENDPOINTS ==============
class ABTestCreate(BaseModel):
    property_id: str
    name: str
    variant_a_name: Optional[str] = "Variante A"
    variant_b_name: Optional[str] = "Variante B"
    variant_a_url: Optional[str] = None
    variant_b_url: Optional[str] = None

class ABTestResponse(BaseModel):
    id: str
    property_id: str
    name: str
    variant_a_name: str
    variant_b_name: str
    variant_a_url: Optional[str]
    variant_b_url: Optional[str]
    active: bool
    created_at: str
    updated_at: str


# ============== PARTNER API MODELS ==============
class PartnerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    commission_rate: Optional[float] = 0
    is_active: Optional[bool] = True

class PartnerResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    category: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    commission_rate: float
    is_active: bool
    created_at: str


# ============== SMART RULES API MODELS ==============
class SmartRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    condition: str
    action: str
    priority: Optional[int] = 0
    is_active: Optional[bool] = True

class SmartRuleResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    trigger_type: str
    condition: str
    action: str
    priority: int
    is_active: bool
    created_at: str

@api_router.get("/ab-tests", response_model=List[ABTestResponse], dependencies=[Depends(get_current_user)])
def get_ab_tests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle A/B Tests für den aktuellen User"""
    ab_tests = db.query(ABTest).filter(ABTest.property_id.in_(
        db.query(Property.id).filter(Property.user_id == user.id)
    )).all()
    return ab_tests

@api_router.post("/ab-tests", response_model=ABTestResponse, dependencies=[Depends(get_current_user)])
def create_ab_test(ab_test: ABTestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle einen neuen A/B Test"""
    property = db.query(Property).filter(
        Property.id == ab_test.property_id,
        Property.user_id == user.id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property nicht gefunden oder nicht berechtigt")
    
    ab_test_obj = ABTest(
        id=str(uuid.uuid4()),
        property_id=ab_test.property_id,
        name=ab_test.name,
        variant_a_name=ab_test.variant_a_name,
        variant_b_name=ab_test.variant_b_name,
        variant_a_url=ab_test.variant_a_url,
        variant_b_url=ab_test.variant_b_url,
        active=False
    )
    db.add(ab_test_obj)
    db.commit()
    db.refresh(ab_test_obj)
    return ab_test_obj

@api_router.put("/ab-tests/{ab_test_id}", response_model=ABTestResponse, dependencies=[Depends(get_current_user)])
def update_ab_test(ab_test_id: str, ab_test: ABTestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere einen A/B Test"""
    db_ab_test = db.query(ABTest).filter(
        ABTest.id == ab_test_id,
        ABTest.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_ab_test:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden")
    
    db_ab_test.name = ab_test.name
    db_ab_test.variant_a_name = ab_test.variant_a_name
    db_ab_test.variant_b_name = ab_test.variant_b_name
    db_ab_test.variant_a_url = ab_test.variant_a_url
    db_ab_test.variant_b_url = ab_test.variant_b_url
    db.commit()
    db.refresh(db_ab_test)
    return db_ab_test

@api_router.delete("/ab-tests/{ab_test_id}", dependencies=[Depends(get_current_user)])
def delete_ab_test(ab_test_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche einen A/B Test"""
    db_ab_test = db.query(ABTest).filter(
        ABTest.id == ab_test_id,
        ABTest.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_ab_test:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden")
    
    db.delete(db_ab_test)
    db.commit()
    return {"message": "A/B Test gelöscht"}


# ============== PARTNER API ENDPOINTS ==============
from database import Partner as DBPartner, SmartRule as DBSmartRule

@api_router.get("/partners", response_model=List[PartnerResponse], dependencies=[Depends(get_current_user)])
def get_partners(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Partner für den aktuellen User"""
    partners = db.query(DBPartner).filter(DBPartner.user_id == user.id).all()
    return partners

@api_router.post("/partners", response_model=PartnerResponse, dependencies=[Depends(get_current_user)])
def create_partner(partner: PartnerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle einen neuen Partner"""
    partner_obj = DBPartner(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=partner.name,
        description=partner.description,
        category=partner.category,
        address=partner.address,
        phone=partner.phone,
        email=partner.email,
        website=partner.website,
        image_url=partner.image_url,
        commission_rate=partner.commission_rate or 0,
        is_active=partner.is_active if partner.is_active is not None else True
    )
    db.add(partner_obj)
    db.commit()
    db.refresh(partner_obj)
    return partner_obj

@api_router.put("/partners/{partner_id}", response_model=PartnerResponse, dependencies=[Depends(get_current_user)])
def update_partner(partner_id: str, partner: PartnerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere einen Partner"""
    db_partner = db.query(DBPartner).filter(
        DBPartner.id == partner_id,
        DBPartner.user_id == user.id
    ).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner nicht gefunden")
    
    db_partner.name = partner.name
    db_partner.description = partner.description
    db_partner.category = partner.category
    db_partner.address = partner.address
    db_partner.phone = partner.phone
    db_partner.email = partner.email
    db_partner.website = partner.website
    db_partner.image_url = partner.image_url
    db_partner.commission_rate = partner.commission_rate or 0
    db_partner.is_active = partner.is_active if partner.is_active is not None else db_partner.is_active
    db.commit()
    db.refresh(db_partner)
    return db_partner

@api_router.delete("/partners/{partner_id}", dependencies=[Depends(get_current_user)])
def delete_partner(partner_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche einen Partner"""
    db_partner = db.query(DBPartner).filter(
        DBPartner.id == partner_id,
        DBPartner.user_id == user.id
    ).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner nicht gefunden")
    
    db.delete(db_partner)
    db.commit()
    return {"message": "Partner gelöscht"}


# ============== SMART RULES API ENDPOINTS ==============
@api_router.get("/smart-rules", response_model=List[SmartRuleResponse], dependencies=[Depends(get_current_user)])
def get_smart_rules(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Smart Rules für den aktuellen User"""
    smart_rules = db.query(DBSmartRule).filter(DBSmartRule.user_id == user.id).order_by(DBSmartRule.priority).all()
    return smart_rules

@api_router.post("/smart-rules", response_model=SmartRuleResponse, dependencies=[Depends(get_current_user)])
def create_smart_rule(smart_rule: SmartRuleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle eine neue Smart Rule"""
    smart_rule_obj = DBSmartRule(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=smart_rule.name,
        description=smart_rule.description,
        trigger_type=smart_rule.trigger_type,
        condition=smart_rule.condition,
        action=smart_rule.action,
        priority=smart_rule.priority or 0,
        is_active=smart_rule.is_active if smart_rule.is_active is not None else True
    )
    db.add(smart_rule_obj)
    db.commit()
    db.refresh(smart_rule_obj)
    return smart_rule_obj

@api_router.put("/smart-rules/{smart_rule_id}", response_model=SmartRuleResponse, dependencies=[Depends(get_current_user)])
def update_smart_rule(smart_rule_id: str, smart_rule: SmartRuleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere eine Smart Rule"""
    db_smart_rule = db.query(DBSmartRule).filter(
        DBSmartRule.id == smart_rule_id,
        DBSmartRule.user_id == user.id
    ).first()
    if not db_smart_rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    db_smart_rule.name = smart_rule.name
    db_smart_rule.description = smart_rule.description
    db_smart_rule.trigger_type = smart_rule.trigger_type
    db_smart_rule.condition = smart_rule.condition
    db_smart_rule.action = smart_rule.action
    db_smart_rule.priority = smart_rule.priority or 0
    db_smart_rule.is_active = smart_rule.is_active if smart_rule.is_active is not None else db_smart_rule.is_active
    db.commit()
    db.refresh(db_smart_rule)
    return db_smart_rule

@api_router.delete("/smart-rules/{smart_rule_id}", dependencies=[Depends(get_current_user)])
def delete_smart_rule(smart_rule_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche eine Smart Rule"""
    db_smart_rule = db.query(DBSmartRule).filter(
        DBSmartRule.id == smart_rule_id,
        DBSmartRule.user_id == user.id
    ).first()
    if not db_smart_rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    db.delete(db_smart_rule)
    db.commit()
    return {"message": "Smart Rule gelöscht"}


@api_router.patch("/ab-tests/{ab_test_id}/activate", response_model=ABTestResponse, dependencies=[Depends(get_current_user)])
def activate_ab_test(ab_test_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktiviere einen A/B Test (deaktiviert andere für dieselbe Property)"""
    db_ab_test = db.query(ABTest).filter(
        ABTest.id == ab_test_id,
        ABTest.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_ab_test:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden")
    
    # Deaktiviere andere Tests für dieselbe Property
    db.query(ABTest).filter(
        ABTest.property_id == db_ab_test.property_id,
        ABTest.id != ab_test_id
    ).update({ABTest.active: False})
    
    db_ab_test.active = not db_ab_test.active  # Toggle
    db.commit()
    db.refresh(db_ab_test)
    return db_ab_test

# ============== END A/B TESTING API ENDPOINTS ==============

# ============== STORE CONFIGURATOR API ENDPOINTS ==============
class ExtraCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int = 0
    stock: int = 0
    image_url: Optional[str] = None
    is_active: bool = True

class ExtraResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str]
    is_active: bool
    created_at: str

@api_router.get("/extras", response_model=List[ExtraResponse], dependencies=[Depends(get_current_user)])
def get_extras(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Extras für den aktuellen User"""
    extras = db.query(Extra).filter(Extra.user_id == user.id).all()
    return extras

@api_router.post("/extras", response_model=ExtraResponse, dependencies=[Depends(get_current_user)])
def create_extra(extra: ExtraCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle ein neues Extra (Upsell)"""
    extra_obj = Extra(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=extra.name,
        description=extra.description,
        price=extra.price,
        stock=extra.stock,
        image_url=extra.image_url,
        is_active=extra.is_active
    )
    db.add(extra_obj)
    db.commit()
    db.refresh(extra_obj)
    return extra_obj

@api_router.put("/extras/{extra_id}", response_model=ExtraResponse, dependencies=[Depends(get_current_user)])
def update_extra(extra_id: str, extra: ExtraCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere ein Extra"""
    db_extra = db.query(Extra).filter(
        Extra.id == extra_id,
        Extra.user_id == user.id
    ).first()
    if not db_extra:
        raise HTTPException(status_code=404, detail="Extra nicht gefunden")
    
    db_extra.name = extra.name
    db_extra.description = extra.description
    db_extra.price = extra.price
    db_extra.stock = extra.stock
    db_extra.image_url = extra.image_url
    db_extra.is_active = extra.is_active
    db.commit()
    db.refresh(db_extra)
    return db_extra

@api_router.delete("/extras/{extra_id}", dependencies=[Depends(get_current_user)])
def delete_extra(extra_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche ein Extra"""
    db_extra = db.query(Extra).filter(
        Extra.id == extra_id,
        Extra.user_id == user.id
    ).first()
    if not db_extra:
        raise HTTPException(status_code=404, detail="Extra nicht gefunden")
    
    db.delete(db_extra)
    db.commit()
    return {"message": "Extra gelöscht"}

# Bundle Endpoints
class BundleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int = 0
    is_active: bool = True

class BundleResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    price: int
    is_active: bool
    created_at: str

@api_router.get("/bundles", response_model=List[BundleResponse], dependencies=[Depends(get_current_user)])
def get_bundles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Bundles für den aktuellen User"""
    bundles = db.query(Bundle).filter(Bundle.user_id == user.id).all()
    return bundles

@api_router.post("/bundles", response_model=BundleResponse, dependencies=[Depends(get_current_user)])
def create_bundle(bundle: BundleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle ein neues Bundle"""
    bundle_obj = Bundle(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=bundle.name,
        description=bundle.description,
        price=bundle.price,
        is_active=bundle.is_active
    )
    db.add(bundle_obj)
    db.commit()
    db.refresh(bundle_obj)
    return bundle_obj

@api_router.put("/bundles/{bundle_id}", response_model=BundleResponse, dependencies=[Depends(get_current_user)])
def update_bundle(bundle_id: str, bundle: BundleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere ein Bundle"""
    db_bundle = db.query(Bundle).filter(
        Bundle.id == bundle_id,
        Bundle.user_id == user.id
    ).first()
    if not db_bundle:
        raise HTTPException(status_code=404, detail="Bundle nicht gefunden")
    
    db_bundle.name = bundle.name
    db_bundle.description = bundle.description
    db_bundle.price = bundle.price
    db_bundle.is_active = bundle.is_active
    db.commit()
    db.refresh(db_bundle)
    return db_bundle

@api_router.delete("/bundles/{bundle_id}", dependencies=[Depends(get_current_user)])
def delete_bundle(bundle_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche ein Bundle"""
    db_bundle = db.query(Bundle).filter(
        Bundle.id == bundle_id,
        Bundle.user_id == user.id
    ).first()
    if not db_bundle:
        raise HTTPException(status_code=404, detail="Bundle nicht gefunden")
    
    db.delete(db_bundle)
    db.commit()
    return {"message": "Bundle gelöscht"}

# Bundle Extra Management
class BundleExtraCreate(BaseModel):
    extra_id: str
    quantity: int = 1

@api_router.post("/bundles/{bundle_id}/extras", dependencies=[Depends(get_current_user)])
def add_bundle_extra(bundle_id: str, bundle_extra: BundleExtraCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Füge ein Extra zu einem Bundle hinzu"""
    db_bundle = db.query(Bundle).filter(
        Bundle.id == bundle_id,
        Bundle.user_id == user.id
    ).first()
    if not db_bundle:
        raise HTTPException(status_code=404, detail="Bundle nicht gefunden")
    
    # Prüfe ob Extra existiert
    db_extra = db.query(Extra).filter(
        Extra.id == bundle_extra.extra_id,
        Extra.user_id == user.id
    ).first()
    if not db_extra:
        raise HTTPException(status_code=404, detail="Extra nicht gefunden")
    
    bundle_extra_obj = BundleExtra(
        id=str(uuid.uuid4()),
        bundle_id=bundle_id,
        extra_id=bundle_extra.extra_id,
        quantity=bundle_extra.quantity
    )
    db.add(bundle_extra_obj)
    db.commit()
    return {"message": "Extra zum Bundle hinzugefügt"}

@api_router.delete("/bundles/{bundle_id}/extras/{extra_id}", dependencies=[Depends(get_current_user)])
def remove_bundle_extra(bundle_id: str, extra_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Entferne ein Extra aus einem Bundle"""
    db_bundle_extra = db.query(BundleExtra).filter(
        BundleExtra.bundle_id == bundle_id,
        BundleExtra.extra_id == extra_id
    ).first()
    if not db_bundle_extra:
        raise HTTPException(status_code=404, detail="Bundle-Extra nicht gefunden")
    
    db.delete(db_bundle_extra)
    db.commit()
    return {"message": "Extra aus Bundle entfernt"}

# ============== END STORE CONFIGURATOR API ENDPOINTS ==============

# ============== PARTNER API ENDPOINTS ==============
class PartnerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    commission_rate: Optional[float] = 0
    is_active: Optional[bool] = True

class PartnerResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    image_url: Optional[str]
    commission_rate: float
    is_active: bool
    created_at: str

@api_router.get("/partners", response_model=List[PartnerResponse], dependencies=[Depends(get_current_user)])
def get_partners(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Partner für den aktuellen User"""
    from database import Partner
    partners = db.query(Partner).filter(Partner.user_id == user.id).all()
    return partners

@api_router.post("/partners", response_model=PartnerResponse, dependencies=[Depends(get_current_user)])
def create_partner(partner: PartnerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle einen neuen Partner"""
    from database import Partner
    partner_obj = Partner(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=partner.name,
        description=partner.description,
        category=partner.category,
        address=partner.address,
        phone=partner.phone,
        email=partner.email,
        website=partner.website,
        image_url=partner.image_url,
        commission_rate=partner.commission_rate or 0,
        is_active=partner.is_active if partner.is_active is not None else True
    )
    db.add(partner_obj)
    db.commit()
    db.refresh(partner_obj)
    return partner_obj

@api_router.put("/partners/{partner_id}", response_model=PartnerResponse, dependencies=[Depends(get_current_user)])
def update_partner(partner_id: str, partner: PartnerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere einen Partner"""
    from database import Partner
    db_partner = db.query(Partner).filter(
        Partner.id == partner_id,
        Partner.user_id == user.id
    ).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner nicht gefunden")
    
    db_partner.name = partner.name
    db_partner.description = partner.description
    db_partner.category = partner.category
    db_partner.address = partner.address
    db_partner.phone = partner.phone
    db_partner.email = partner.email
    db_partner.website = partner.website
    db_partner.image_url = partner.image_url
    db_partner.commission_rate = partner.commission_rate or 0
    db_partner.is_active = partner.is_active if partner.is_active is not None else db_partner.is_active
    db.commit()
    db.refresh(db_partner)
    return db_partner

@api_router.delete("/partners/{partner_id}", dependencies=[Depends(get_current_user)])
def delete_partner(partner_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche einen Partner"""
    from database import Partner
    db_partner = db.query(Partner).filter(
        Partner.id == partner_id,
        Partner.user_id == user.id
    ).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner nicht gefunden")
    
    db.delete(db_partner)
    db.commit()
    return {"message": "Partner gelöscht"}


# ============== SMART RULES API ENDPOINTS ==============
class SmartRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    condition: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = 0
    is_active: Optional[bool] = True

class SmartRuleResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    trigger_type: Optional[str]
    condition: Optional[str]
    action: Optional[str]
    priority: int
    is_active: bool
    created_at: str

@api_router.get("/smart-rules", response_model=List[SmartRuleResponse], dependencies=[Depends(get_current_user)])
def get_smart_rules(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Smart Rules für den aktuellen User"""
    from database import SmartRule
    smart_rules = db.query(SmartRule).filter(SmartRule.user_id == user.id).all()
    return smart_rules

@api_router.post("/smart-rules", response_model=SmartRuleResponse, dependencies=[Depends(get_current_user)])
def create_smart_rule(rule: SmartRuleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle eine neue Smart Rule"""
    from database import SmartRule
    rule_obj = SmartRule(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type,
        condition=rule.condition,
        action=rule.action,
        priority=rule.priority or 0,
        is_active=rule.is_active if rule.is_active is not None else True
    )
    db.add(rule_obj)
    db.commit()
    db.refresh(rule_obj)
    return rule_obj

@api_router.put("/smart-rules/{rule_id}", response_model=SmartRuleResponse, dependencies=[Depends(get_current_user)])
def update_smart_rule(rule_id: str, rule: SmartRuleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere eine Smart Rule"""
    from database import SmartRule
    db_rule = db.query(SmartRule).filter(
        SmartRule.id == rule_id,
        SmartRule.user_id == user.id
    ).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    db_rule.name = rule.name
    db_rule.description = rule.description
    db_rule.trigger_type = rule.trigger_type
    db_rule.condition = rule.condition
    db_rule.action = rule.action
    db_rule.priority = rule.priority or 0
    db_rule.is_active = rule.is_active if rule.is_active is not None else db_rule.is_active
    db.commit()
    db.refresh(db_rule)
    return db_rule

@api_router.delete("/smart-rules/{rule_id}", dependencies=[Depends(get_current_user)])
def delete_smart_rule(rule_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Lösche eine Smart Rule"""
    from database import SmartRule
    db_rule = db.query(SmartRule).filter(
        SmartRule.id == rule_id,
        SmartRule.user_id == user.id
    ).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "Smart Rule gelöscht"}

# ============== END SMART RULES API ENDPOINTS ==============

# ============== CHECKOUT & BOOKING API ENDPOINTS ==============
class BookingCreate(BaseModel):
    property_id: str
    guest_name: str
    guest_email: str
    guest_phone: Optional[str] = None
    check_in: str
    check_out: str
    guests: int
    message: Optional[str] = None
    total_price: float
    tipping_percentage: Optional[int] = 0
    tipping_amount: Optional[float] = 0
    payment_method: Optional[str] = None

class BookingResponse(BaseModel):
    id: str
    property_id: str
    user_id: str
    guest_name: Optional[str]
    guest_email: Optional[str]
    guest_phone: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    guests: Optional[int]
    message: Optional[str]
    total_price: float
    tipping_percentage: int
    tipping_amount: float
    status: str
    payment_method: Optional[str]
    invoice_generated: bool
    created_at: str

@api_router.get("/bookings", response_model=List[BookingResponse], dependencies=[Depends(get_current_user)])
def get_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole alle Buchungen für den aktuellen User"""
    from database import Booking
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return bookings

@api_router.post("/bookings", response_model=BookingResponse, dependencies=[Depends(get_current_user)])
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle eine neue Buchung (Vorab-Validierung)"""
    from database import Booking, Property
    # Prüfe ob Property existiert und dem User gehört
    property = db.query(Property).filter(
        Property.id == booking.property_id,
        Property.user_id == user.id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property nicht gefunden")
    
    # Validate dates
    try:
        check_in = datetime.fromisoformat(booking.check_in.replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(booking.check_out.replace('Z', '+00:00'))
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Check-in muss vor Check-out liegen")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültiges Datumsformat: {str(e)}")
    
    booking_obj = Booking(
        id=str(uuid.uuid4()),
        property_id=booking.property_id,
        user_id=user.id,
        guest_name=booking.guest_name,
        guest_email=booking.guest_email,
        guest_phone=booking.guest_phone,
        check_in=check_in,
        check_out=check_out,
        guests=booking.guests,
        message=booking.message,
        total_price=booking.total_price,
        tipping_percentage=booking.tipping_percentage or 0,
        tipping_amount=booking.tipping_amount or 0,
        status='pending',
        payment_method=booking.payment_method,
        invoice_generated=False
    )
    db.add(booking_obj)
    db.commit()
    db.refresh(booking_obj)
    return booking_obj

@api_router.post("/checkout/validate", dependencies=[Depends(get_current_user)])
def validate_checkout(booking: BookingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Validiere Checkout-Daten (ohne Buchung zu erstellen)"""
    from database import Property
    property = db.query(Property).filter(
        Property.id == booking.property_id,
        Property.user_id == user.id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property nicht gefunden")
    
    try:
        check_in = datetime.fromisoformat(booking.check_in.replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(booking.check_out.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat")
    
    return {
        "valid": True,
        "property_name": property.name,
        "total_price": booking.total_price,
        "tipping_amount": booking.tipping_amount or 0,
        "final_total": booking.total_price + (booking.tipping_amount or 0)
    }

@api_router.get("/bookings/{booking_id}/invoice", dependencies=[Depends(get_current_user)])
def get_booking_invoice(booking_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole Rechnung als PDF für eine Buchung"""
    from database import Booking, Property
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
    
    # Generiere PDF-Rechnung
    # Hier würde der eigentliche PDF-Generierungs-Code stehen
    # Für MVP return dummy PDF response
    return {
        "booking_id": booking.id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "download_url": f"/api/bookings/{booking_id}/invoice/download",
        "status": "ready"
    }

@api_router.post("/bookings/{booking_id}/confirm", response_model=BookingResponse, dependencies=[Depends(get_current_user)])
def confirm_booking(booking_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Buchung endgültig bestätigen"""
    from database import Booking
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
    
    booking.status = 'confirmed'
    booking.invoice_generated = True
    db.commit()
    db.refresh(booking)
    return booking


# ============== END CHECKOUT & BOOKING API ENDPOINTS ==============

# ============== CLEANER & TASK API ENDPOINTS ==============
class CleanerLoginRequest(BaseModel):
    cleaner_id: str

class CleanerResponse(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    property_ids: List[str]
    created_at: str

@api_router.post("/cleaner/login")
def cleaner_login(request: CleanerLoginRequest, db: Session = Depends(get_db)):
    """Cleaner anmelden (passwortloser Login via cleanerId)"""
    # Hier würde die Validierung der cleanerId stattfinden
    # Für MVP return dummy response
    return {
        "success": True,
        "cleaner_id": request.cleaner_id,
        "message": "Cleaner erfolgreich angemeldet"
    }

@api_router.get("/cleaner/profile")
def get_cleaner_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Cleaner Profil holen"""
    # Hier würde das echte Profil aus der DB geladen
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": None,
        "property_ids": []
    }


class TaskCreate(BaseModel):
    property_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[int] = 0

class TaskResponse(BaseModel):
    id: str
    property_id: str
    cleaner_id: Optional[str]
    title: str
    description: Optional[str]
    due_date: Optional[str]
    completed: bool
    priority: int
    created_at: str

@api_router.get("/tasks", response_model=List[TaskResponse], dependencies=[Depends(get_current_user)])
def get_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user), property_id: Optional[str] = None):
    """Hole alle Aufgaben für den aktuellen User"""
    from database import Task
    query = db.query(Task).filter(Task.property_id.in_(
        db.query(Property.id).filter(Property.user_id == user.id)
    ))
    if property_id:
        query = query.filter(Task.property_id == property_id)
    tasks = query.all()
    return tasks

@api_router.post("/tasks", response_model=TaskResponse, dependencies=[Depends(get_current_user)])
def create_task(task: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Erstelle eine neue Aufgabe"""
    from database import Task, Property
    # Prüfe ob Property existiert und dem User gehört
    property = db.query(Property).filter(
        Property.id == task.property_id,
        Property.user_id == user.id
    ).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property nicht gefunden")
    
    due_date = None
    if task.due_date:
        try:
            due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiges Datumsformat")
    
    task_obj = Task(
        id=str(uuid.uuid4()),
        property_id=task.property_id,
        cleaner_id=None,  # Wird beim Zuweisen gesetzt
        title=task.title,
        description=task.description,
        due_date=due_date,
        completed=False,
        priority=task.priority or 0
    )
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj

@api_router.put("/tasks/{task_id}", response_model=TaskResponse, dependencies=[Depends(get_current_user)])
def update_task(task_id: str, task: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere eine Aufgabe"""
    from database import Task
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority or 0
    
    if task.due_date:
        try:
            db_task.due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiges Datumsformat")
    
    db.commit()
    db.refresh(db_task)
    return db_task

@api_router.post("/tasks/{task_id}/complete", response_model=TaskResponse, dependencies=[Depends(get_current_user)])
def complete_task(task_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Markiere eine Aufgabe als erledigt"""
    from database import Task
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.property_id.in_(
            db.query(Property.id).filter(Property.user_id == user.id)
        )
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")
    
    db_task.completed = True
    db.commit()
    db.refresh(db_task)
    return db_task

@api_router.get("/tasks/export/ics", dependencies=[Depends(get_current_user)])
def export_tasks_ics(db: Session = Depends(get_db), user: User = Depends(get_current_user), property_id: Optional[str] = None):
    """Exportiere Aufgaben als .ics Datei"""
    from database import Task
    # Hole alle Aufgaben
    query = db.query(Task).filter(Task.property_id.in_(
        db.query(Property.id).filter(Property.user_id == user.id)
    ))
    if property_id:
        query = query.filter(Task.property_id == property_id)
    tasks = query.all()
    
    # Erstelle .ics content
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Welcome Link//Tasks//DE
"""
    for task in tasks:
        ics_content += f"""BEGIN:VEVENT
SUMMARY:{task.title}
DESCRIPTION:{task.description or ''}
DTSTART:{task.due_date.strftime('%Y%m%dT%H%M%S') if task.due_date else datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}
DTEND:{(task.due_date + timedelta(hours=1) if task.due_date else datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')}
STATUS:{"COMPLETED" if task.completed else "NEEDS-ACTION"}
END:VEVENT
"""
    ics_content += "END:VCALENDAR"
    
    from fastapi.responses import Response
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=tasks.ics"}
    )


# ============== END CLEANER & TASK API ENDPOINTS ==============

# ============== GLOBAL STATS & MONITORING API ENDPOINTS ==============
from pydantic import BaseModel
from typing import List, Optional, Dict

class GlobalStatsResponse(BaseModel):
    total_hosts: int
    total_properties: int
    total_bookings: int
    total_revenue: float
    active_bookings_today: int
    completed_bookings_today: int
    updated_at: str

@api_router.get("/stats/global", response_model=GlobalStatsResponse, dependencies=[Depends(get_current_user)])
def get_global_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole globale Plattform-Statistiken (nur für Admins oder alle User)"""
    from database import User, Property, Booking
    
    # Zähle alle User (Hosts)
    total_hosts = db.query(User).count()
    
    # Zähle alle Properties
    total_properties = db.query(Property).count()
    
    # Zähle alle Buchungen
    total_bookings = db.query(Booking).count()
    
    # Berechne Gesamtumsatz
    total_revenue_result = db.query(db.func.sum(Booking.total_price)).scalar()
    total_revenue = total_revenue_result or 0.0
    
    # Zähle aktive Buchungen heute
    from datetime import datetime, date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    
    active_bookings_today = db.query(Booking).filter(
        Booking.created_at >= today_start,
        Booking.created_at < today_end
    ).count()
    
    completed_bookings_today = db.query(Booking).filter(
        Booking.created_at >= today_start,
        Booking.created_at < today_end,
        Booking.status == 'confirmed'
    ).count()
    
    return GlobalStatsResponse(
        total_hosts=total_hosts,
        total_properties=total_properties,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        active_bookings_today=active_bookings_today,
        completed_bookings_today=completed_bookings_today,
        updated_at=datetime.now(timezone.utc).isoformat()
    )


# ============== END GLOBAL STATS & MONITORING API ENDPOINTS ==============

# ============== BRANDING & AI API ENDPOINTS ==============
from pydantic import BaseModel
from typing import List, Optional, Dict

class BrandingResponse(BaseModel):
    brand_color: str
    logo_url: Optional[str]
    updated_at: str

@api_router.get("/branding", response_model=BrandingResponse, dependencies=[Depends(get_current_user)])
def get_branding(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Hole Branding-Konfiguration für den aktuellen User"""
    return BrandingResponse(
        brand_color=user.brand_color or '#F27C2C',
        logo_url=user.logo_url,
        updated_at=user.created_at.isoformat()
    )

class BrandingUpdate(BaseModel):
    brand_color: Optional[str] = '#F27C2C'
    logo_url: Optional[str] = None

@api_router.put("/branding", response_model=BrandingResponse, dependencies=[Depends(get_current_user)])
def update_branding(branding: BrandingUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Aktualisiere Branding-Konfiguration"""
    user.brand_color = branding.brand_color
    user.logo_url = branding.logo_url
    db.commit()
    db.refresh(user)
    return BrandingResponse(
        brand_color=user.brand_color,
        logo_url=user.logo_url,
        updated_at=user.created_at.isoformat()
    )


class AICopyRequest(BaseModel):
    prompt: str
    language: Optional[str] = "de"

class AICopyResponse(BaseModel):
    text: str
    model: str
    tokens_used: int

@api_router.post("/ai/copywriter", response_model=AICopyResponse, dependencies=[Depends(get_current_user)])
def ai_copywriter(request: AICopyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Generiere Text mit AI (Mock für MVP)"""
    # Hier würde der echte AI Call hin (z.B. mit Anthropic/LLaMA)
    # Für MVP return dummy response
    return AICopyResponse(
        text=f"[AI Generated Text]\nPrompt: {request.prompt}\nLanguage: {request.language}\n\nDies ist ein Mock-Antwort für den MVP.",
        model="mock-ai-v1",
        tokens_used=150
    )


# ============== END BRANDING & AI API ENDPOINTS ==============

@app.on_event("startup")
def startup():
    """Initialisiere Demo-Benutzer beim Start"""
    try:
        logger.info("🚀 Startup-Event: Initialisiere DB...")
        if not SessionLocal:
            logger.info("DB nicht initialisiert, rufe init_db() auf...")
            init_db()
        
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
