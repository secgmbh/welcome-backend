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
from database import init_db, get_db, User as DBUser, Property as DBProperty, StatusCheck as DBStatusCheck, GuestView as DBGuestView

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


@api_router.get("/guestview-public-qr-data")
def get_guestview_public_qr_data(db: Session = Depends(get_db)):
    """Öffentlicher Endpoint für QR Code Daten (ohne Auth) - für Demo"""
    from sqlalchemy import text as sql_text
    try:
        # Hole Demo-User anhand E-Mail (zuverlässiger als ID)
        demo_email = "demo@welcome-link.de"
        user = db.query(DBUser).filter(DBUser.email == demo_email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Demo-User {demo_email} nicht gefunden")
        
        # Hole Properties - nutze text() für flexible Spaltenabfrage
        # Prüfe ob description Spalte existiert
        try:
            result = db.execute(sql_text("SELECT column_name FROM information_schema.columns WHERE table_name = 'properties' AND column_name = 'description'")).fetchone()
            has_description = result is not None
        except:
            has_description = False
        
        if has_description:
            properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
        else:
            # Ohne description Spalte - nutze text() für SQL
            # CAST user_id immer zu VARCHAR um UUID vs Integer zu umgehen
            stmt = sql_text("SELECT id, user_id, name, address, created_at FROM properties WHERE CAST(user_id AS VARCHAR) = :user_id")
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


@api_router.get("/guestview-qr-data")
def get_guestview_qr_data(db: Session = Depends(get_db)):
    """Öffentlicher Endpoint für QR Code Daten - direkte Abfrage ohne description"""
    from sqlalchemy import text as sql_text
    try:
        demo_email = "demo@welcome-link.de"
        user = db.query(DBUser).filter(DBUser.email == demo_email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Demo-User {demo_email} nicht gefunden")
        
        # hole Properties mit raw SQL - direkt in SQL String (keine Parameter)
        stmt = sql_text("SELECT id, user_id, name, address, created_at FROM properties WHERE user_id = '3e6b2efc-e463-4bb5-b6df-3da7e9708048'")
        sql_result = db.execute(stmt).fetchall()
        
        properties = []
        for row in sql_result:
            p = type('Property', (), {})()
            p.id = str(row.id) if row.id else None
            p.user_id = str(row.user_id) if row.user_id else None
            p.name = row.name
            p.address = row.address
            p.created_at = row.created_at
            p.description = None
            properties.append(p)
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://www.welcome-link.de')
        qr_url = f"{frontend_url}/guestview/demo-guest-view-token"
        
        result = []
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
        
        logger.info(f"QR Daten zurückgegeben für {len(properties)} Properties")
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Fehler beim Abrufen der QR-Daten: {str(e)}"
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
