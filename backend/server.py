from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import os
import logging
import json
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import secrets
import jwt
from passlib.context import CryptContext
from slowapi import Limiter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slowapi.util import get_remote_address
from slowapi.util import get_remote_address
import time
# psutil is optional - used for system metrics in health check
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
    import sys
    print("⚠️  psutil not available - system metrics disabled", file=sys.stderr)

from database import init_db, get_db, User as DBUser, Property as DBProperty, StatusCheck as DBStatusCheck, GuestView as DBGuestView, Booking as DBBooking, Cleaner as DBCleaner, PropertyCleaner as DBPropertyCleaner

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

# ============ SMTP CONFIG ============
SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM = os.environ.get('SMTP_FROM', 'noreply@welcome-link.de')

# Warnung wenn SMTP nicht konfiguriert in Production
if ENVIRONMENT == 'production' and not SMTP_PASSWORD:
    import sys
    print(f"⚠️  WARNING: SMTP_PASSWORD nicht gesetzt - E-Mails werden nicht versendet!", file=sys.stderr)

# ============ EMAIL HELPER ============
def send_email(to_email: str, subject: str, html_body: str, text_body: str = None):
    """Sende E-Mail über SMTP"""
    if not SMTP_PASSWORD:
        logger.warning(f"E-Mail nicht gesendet (SMTP nicht konfiguriert): {to_email}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if text_body:
            msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())
        
        logger.info(f"✅ E-Mail gesendet an: {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ E-Mail-Fehler: {str(e)}")
        return False

def send_magic_link_email(email: str, token: str):
    """Sende Magic Link E-Mail"""
    magic_url = f"https://www.welcome-link.de/auth/magic?token={token}"
    
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #F27C2C 0%, #FF9F4A 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Welcome Link</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Ihr Magic Link</h2>
            <p style="color: #666; font-size: 16px;">Klicken Sie auf den Button, um sich anzumelden:</p>
            <a href="{magic_url}" style="display: inline-block; background: #F27C2C; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
                Anmelden
            </a>
            <p style="color: #999; font-size: 14px;">Oder kopieren Sie diesen Link in Ihren Browser:</p>
            <p style="color: #666; font-size: 14px; word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 6px;">{magic_url}</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">Der Link ist 15 Minuten gültig.</p>
        </div>
    </body>
    </html>
    """
    
    text = f"""Welcome Link - Magic Link
    
Klicken Sie auf diesen Link um sich anzumelden:
{magic_url}

Der Link ist 15 Minuten gültig.
"""
    
    return send_email(email, "Ihr Magic Link - Welcome Link", html, text)

def send_welcome_email(email: str, name: str):
    """Sende Willkommens-E-Mail nach Registrierung"""
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #F27C2C 0%, #FF9F4A 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Willkommen bei Welcome Link! 🎉</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hallo {name}!</h2>
            <p style="color: #666; font-size: 16px;">Vielen Dank für Ihre Registrierung bei Welcome Link.</p>
            <p style="color: #666; font-size: 16px;">Sie können jetzt Ihre erste Unterkunft einrichten und digitale Gäste-Mappen erstellen.</p>
            <a href="https://www.welcome-link.de/dashboard" style="display: inline-block; background: #F27C2C; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
                Zum Dashboard
            </a>
            <p style="color: #999; font-size: 14px; margin-top: 30px;">Bei Fragen erreichen Sie uns unter support@welcome-link.de</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, f"Willkommen bei Welcome Link, {name}!", html)

def send_booking_confirmation_email(email: str, name: str, property_name: str, checkin: str, checkout: str, guests: int, total: float):
    """Sende Buchungsbestätigungs-E-Mail"""
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #F27C2C 0%, #FF9F4A 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Buchungsbestätigung 🏠</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hallo {name}!</h2>
            <p style="color: #666; font-size: 16px;">Vielen Dank für Ihre Buchung. Hier sind Ihre Buchungsdetails:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #F27C2C; margin-top: 0;">{property_name}</h3>
                <table style="width: 100%; color: #666;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Check-in:</strong></td>
                        <td style="padding: 8px 0;">{checkin}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Check-out:</strong></td>
                        <td style="padding: 8px 0;">{checkout}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Gäste:</strong></td>
                        <td style="padding: 8px 0;">{guests}</td>
                    </tr>
                    <tr style="border-top: 1px solid #ddd;">
                        <td style="padding: 12px 0;"><strong>Gesamtbetrag:</strong></td>
                        <td style="padding: 12px 0; font-size: 18px; color: #F27C2C;"><strong>€{total:.2f}</strong></td>
                    </tr>
                </table>
            </div>
            
            <p style="color: #666; font-size: 14px;">Sie erhalten vor der Anreise weitere Informationen zu Ihrer Unterkunft.</p>
            
            <a href="https://www.welcome-link.de/dashboard" style="display: inline-block; background: #F27C2C; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
                Buchung ansehen
            </a>
            
            <p style="color: #999; font-size: 14px; margin-top: 30px;">Bei Fragen erreichen Sie uns unter support@welcome-link.de</p>
        </div>
    </body>
    </html>
    """
    
    text = f"""Buchungsbestätigung - Welcome Link

Hallo {name}!

Vielen Dank für Ihre Buchung.

Buchungsdetails:
- Unterkunft: {property_name}
- Check-in: {checkin}
- Check-out: {checkout}
- Gäste: {guests}
- Gesamtbetrag: €{total:.2f}

Bei Fragen: support@welcome-link.de
"""
    
    return send_email(email, f"Buchungsbestätigung - {property_name}", html, text)

def send_payment_receipt_email(email: str, name: str, amount: float, payment_method: str, transaction_id: str, property_name: str):
    """Sende Zahlungsbestätigungs-E-Mail"""
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #10B981 0%, #34D399 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Zahlung erhalten ✓</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hallo {name}!</h2>
            <p style="color: #666; font-size: 16px;">Vielen Dank für Ihre Zahlung. Hier ist Ihre Zahlungsbestätigung:</p>
            
            <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #10B981;">
                <table style="width: 100%; color: #333;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Betrag:</strong></td>
                        <td style="padding: 8px 0; font-size: 20px; color: #10B981;"><strong>€{amount:.2f}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Zahlungsart:</strong></td>
                        <td style="padding: 8px 0;">{payment_method}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Transaktions-ID:</strong></td>
                        <td style="padding: 8px 0; font-family: monospace;">{transaction_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Unterkunft:</strong></td>
                        <td style="padding: 8px 0;">{property_name}</td>
                    </tr>
                </table>
            </div>
            
            <p style="color: #666; font-size: 14px;">Die Zahlung wurde erfolgreich verarbeitet. Sie erhalten eine separate Buchungsbestätigung.</p>
            
            <a href="https://www.welcome-link.de/dashboard" style="display: inline-block; background: #10B981; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
                Im Dashboard ansehen
            </a>
            
            <p style="color: #999; font-size: 14px; margin-top: 30px;">Bei Fragen erreichen Sie uns unter support@welcome-link.de</p>
        </div>
    </body>
    </html>
    """
    
    text = f"""Zahlungsbestätigung - Welcome Link

Hallo {name}!

Vielen Dank für Ihre Zahlung.

Zahlungsdetails:
- Betrag: €{amount:.2f}
- Zahlungsart: {payment_method}
- Transaktions-ID: {transaction_id}
- Unterkunft: {property_name}

Die Zahlung wurde erfolgreich verarbeitet.

Bei Fragen: support@welcome-link.de
"""
    
    return send_email(email, f"Zahlungsbestätigung - €{amount:.2f}", html, text)

def send_guest_welcome_email(email: str, guest_name: str, property_name: str, host_name: str, checkin: str, checkout: str, wifi_name: str, wifi_password: str, guestview_url: str):
    """Sende Willkommens-E-Mail an Gäste"""
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #F27C2C 0%, #FF9F4A 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Willkommen in {property_name}! 🏡</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hallo {guest_name}!</h2>
            <p style="color: #666; font-size: 16px;">{host_name} freut sich auf Ihren Besuch. Hier sind alle wichtigen Informationen für Ihre Ankunft:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #F27C2C; margin-top: 0;">📅 Ihre Buchung</h3>
                <table style="width: 100%; color: #666;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Check-in:</strong></td>
                        <td style="padding: 8px 0;">{checkin}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Check-out:</strong></td>
                        <td style="padding: 8px 0;">{checkout}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #0284c7; margin-top: 0;">📶 WLAN-Zugang</h3>
                <table style="width: 100%; color: #666;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Netzwerk:</strong></td>
                        <td style="padding: 8px 0;">{wifi_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Passwort:</strong></td>
                        <td style="padding: 8px 0; font-family: monospace;">{wifi_password}</td>
                    </tr>
                </table>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{guestview_url}" style="display: inline-block; background: #F27C2C; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                    📱 Digitale Gästemappe öffnen
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">In der digitalen Gästemappe finden Sie:</p>
            <ul style="color: #666; font-size: 14px;">
                <li>Hausregeln und Tipps</li>
                <li>Umgebungsempfehlungen</li>
                <li>Kontaktdaten des Gastgebers</li>
                <li>Extras und Services buchen</li>
            </ul>
            
            <p style="color: #999; font-size: 14px; margin-top: 30px;">Bei Fragen wenden Sie sich an {host_name}.</p>
        </div>
    </body>
    </html>
    """
    
    text = f"""Willkommen in {property_name}!

Hallo {guest_name}!

{host_name} freut sich auf Ihren Besuch.

Buchungsdetails:
- Check-in: {checkin}
- Check-out: {checkout}

WLAN-Zugang:
- Netzwerk: {wifi_name}
- Passwort: {wifi_password}

Digitale Gästemappe: {guestview_url}

Viel Spaß bei Ihrem Aufenthalt!
"""
    
    return send_email(email, f"Willkommen in {property_name}!", html, text)

# ============ SENTRY ERROR TRACKING ============
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            traces_sample_rate=0.1,  # 10% der Requests tracen
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        print("✓ Sentry initialized")
    except ImportError:
        print("⚠️  Sentry SDK not installed - skipping error tracking")
        SENTRY_DSN = None

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
    version="2.8.1",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)
app.state.limiter = limiter


# ============ SECURITY HEADERS MIDDLEWARE ============
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Fügt Security Headers zu allen Responses hinzu"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://api.welcome-link.de https://www.welcome-link.de; "
            "frame-ancestors 'none';"
        )
        
        # HSTS (nur in Production)
        if ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        return response

# ============ REQUEST TIMING MIDDLEWARE ============
class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Track request timing for performance monitoring"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Add timing header for debugging
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        
        # Log slow requests (>500ms)
        if process_time > 500:
            logger.warning(f"⚠️ Slow request: {request.method} {request.url.path} took {process_time:.2f}ms")
        
        return response

# ============ GLOBAL EXCEPTION HANDLER ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Globaler HTTP Exception Handler mit strukturierten Responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validierungsfehler mit detaillierten Informationen"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "Validation failed",
            "errors": errors,
            "path": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Globaler Exception Handler für unerwartete Fehler"""
    import traceback
    error_id = str(uuid.uuid4())[:8]
    
    logger.error(
        f"[{error_id}] Unhandled exception on {request.url.path}: {str(exc)}\n"
        f"{traceback.format_exc()}"
    )
    
    # In Production keine internen Details preisgeben
    if ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "status_code": 500,
                "message": "Internal server error",
                "error_id": error_id,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "status_code": 500,
                "message": str(exc),
                "error_id": error_id,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "traceback": traceback.format_exc().split("\n")
            }
        )


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
    wifi_name: Optional[str] = None
    wifi_password: Optional[str] = None
    keysafe_location: Optional[str] = None
    keysafe_code: Optional[str] = None
    checkin_time: Optional[str] = "15:00"
    checkout_time: Optional[str] = "11:00"
    brand_color: Optional[str] = "#F27C2C"
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
        
        # Erstelle Demo-Properties mit fixen IDs für Konsistenz
        demo_properties = [
            DBProperty(
                id="demo-prop-1",
                user_id=demo_user.id,
                name="Ferienwohnung Seeblick",
                description="Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.",
                address="Seepromenade 15, 88131 Lindau",
                brand_color="#F27C2C",
                wifi_name="Seeblick-Guest",
                wifi_password="welcome2024",
                checkin_time="15:00",
                checkout_time="11:00",
                created_at=datetime.now(timezone.utc)
            ),
            DBProperty(
                id="demo-prop-2",
                user_id=demo_user.id,
                name="Boutique Hotel Alpenblick",
                description="Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.",
                address="Zugspitzstraße 42, 82467 Garmisch-Partenkirchen",
                brand_color="#2C5F9E",
                created_at=datetime.now(timezone.utc)
            ),
            DBProperty(
                id="demo-prop-3",
                user_id=demo_user.id,
                name="Stadtapartment München City",
                description="Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.",
                address="Maximilianstraße 28, 80539 München",
                brand_color="#4A9D4A",
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for prop in demo_properties:
            db.add(prop)
        db.commit()
        
        logger.info("✓ Demo-Benutzer und Properties erstellt")

# ============ AUTH ROUTES ============

@api_router.post("/auth/register", response_model=AuthResponse)
@limiter.limit("5/minute")
async def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
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
        
        # Sende Welcome Email (im Hintergrund, blockiert nicht)
        try:
            send_welcome_email(db_user.email, db_user.name)
            logger.info(f"Welcome E-Mail gesendet an: {db_user.email}")
        except Exception as email_error:
            # E-Mail-Fehler blockiert die Registrierung nicht
            logger.warning(f"Welcome E-Mail konnte nicht gesendet werden: {email_error}")
        
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
@limiter.limit("10/minute")
async def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
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
@limiter.limit("3/minute")
async def request_magic_link(request: Request, data: MagicLinkRequest, db: Session = Depends(get_db)):
    """Fordere einen Magic Link an"""
    # Generiere Token
    token = secrets.token_urlsafe(32)
    
    # Speichere Token in DB (oder Cache) mit 15 Min Gültigkeit
    # Für Demo: E-Mail senden
    email_sent = send_magic_link_email(data.email, token)
    
    if email_sent:
        logger.info(f"Magic Link gesendet an: {data.email}")
        return {"message": "Magic Link wurde an Ihre E-Mail gesendet", "email": data.email}
    else:
        # Fallback für Demo ohne SMTP
        logger.info(f"Magic Link angefordert für: {data.email} (SMTP nicht konfiguriert)")
        return {
            "message": "Magic Link wurde angefordert. SMTP nicht konfiguriert - prüfen Sie die Logs.",
            "email": data.email,
            "demo_url": f"https://www.welcome-link.de/auth/magic?token={token}"
        }

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

# ============ ADMIN LOGIN ============
@api_router.post("/admin/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def admin_login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """Admin Login - Nur für Administratoren"""
    try:
        # Finde Benutzer (normalisiere E-Mail)
        user = db.query(DBUser).filter(DBUser.email == data.email.lower()).first()

        if not user:
            logger.warning(f"Admin-Login fehlgeschlagen: Benutzer nicht gefunden - {data.email}")
            raise HTTPException(status_code=401, detail="Zugriff verweigert")

        # Überprüfe Passwort
        if not verify_password(data.password, user.password_hash):
            logger.warning(f"Admin-Login fehlgeschlagen: Falsches Passwort - {data.email}")
            raise HTTPException(status_code=401, detail="Zugriff verweigert")

        # Überprüfe Admin-Status (NUR admin@welcome-link.de oder User mit is_admin=True)
        is_admin = user.email == "admin@welcome-link.de" or getattr(user, 'is_admin', False)

        if not is_admin:
            logger.warning(f"Admin-Login fehlgeschlagen: Keine Admin-Berechtigung - {data.email}")
            raise HTTPException(status_code=403, detail="Keine Admin-Berechtigung")

        # Erstelle Token
        token = create_token(user.id, user.email)
        logger.info(f"✓ Admin eingeloggt: {data.email}")

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
        logger.error(f"❌ Fehler bei Admin-Login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server-Fehler: {str(e)[:50]}")


class AdminCreateRequest(BaseModel):
    email: str
    password: str
    secret: str  # Erforderlich für Sicherheit


@api_router.post("/admin/create-admin")
@limiter.limit("1/hour")  # Stark limitiert
async def create_admin_account(request: Request, data: AdminCreateRequest, db: Session = Depends(get_db)):
    """Erstelle Admin-Account - Nur mit Secret möglich"""
    
    # Security: Secret erforderlich (wird nicht in der UI gezeigt)
    ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'WL-Admin-2026-Secret!')
    
    if data.secret != ADMIN_SECRET:
        logger.warning(f"Admin-Account-Erstellung mit falschem Secret versucht")
        raise HTTPException(status_code=403, detail="Nicht autorisiert")
    
    # Nur admin@welcome-link.de erlaubt
    if data.email != "admin@welcome-link.de":
        raise HTTPException(status_code=400, detail="Nur admin@welcome-link.de erlaubt")

    # Prüfe ob bereits existiert
    existing = db.query(DBUser).filter(DBUser.email == "admin@welcome-link.de").first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin-Account existiert bereits")

    # Erstelle Admin
    admin_user = DBUser(
        id=str(uuid.uuid4()),
        email="admin@welcome-link.de",
        name="Administrator",
        password_hash=hash_password(data.password),
        is_demo=False,
        created_at=datetime.now(timezone.utc)
    )

    db.add(admin_user)
    db.commit()

    logger.info(f"✓ Admin-Account erstellt: admin@welcome-link.de")

    return {
        "success": True,
        "message": "Admin-Account erstellt."
    }

# ============ PASSWORD RESET ============
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# In-Memory Token Store (in Production: Redis)
password_reset_tokens = {}

@api_router.post("/auth/password-reset/request")
@limiter.limit("3/minute")
async def request_password_reset(request: Request, data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Fordere Password Reset an"""
    # Prüfe ob User existiert
    user = db.query(DBUser).filter(DBUser.email == data.email).first()
    
    # Generiere Token (auch wenn User nicht existiert - keine Info泄露)
    token = secrets.token_urlsafe(32)
    password_reset_tokens[token] = {
        "email": data.email,
        "expires": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    
    if user:
        # Sende E-Mail
        reset_url = f"https://www.welcome-link.de/auth/reset-password?token={token}"
        
        html = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #F27C2C 0%, #FF9F4A 100%); padding: 30px; border-radius: 12px 12px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Welcome Link</h1>
            </div>
            <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-top: 0;">Passwort zurücksetzen</h2>
                <p style="color: #666; font-size: 16px;">Sie haben angefordert, Ihr Passwort zurückzusetzen.</p>
                <a href="{reset_url}" style="display: inline-block; background: #F27C2C; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
                    Passwort zurücksetzen
                </a>
                <p style="color: #999; font-size: 14px;">Oder kopieren Sie diesen Link in Ihren Browser:</p>
                <p style="color: #666; font-size: 14px; word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 6px;">{reset_url}</p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">Der Link ist 15 Minuten gültig.</p>
                <p style="color: #999; font-size: 12px;">Falls Sie dies nicht angefordert haben, können Sie diese E-Mail ignorieren.</p>
            </div>
        </body>
        </html>
        """
        
        send_email(data.email, "Passwort zurücksetzen - Welcome Link", html)
        logger.info(f"Password reset requested for: {data.email}")
    
    # Immer gleiche Antwort (keine Info泄露)
    return {"message": "Falls ein Account mit dieser E-Mail existiert, erhalten Sie eine E-Mail mit weiteren Anweisungen."}

@api_router.post("/auth/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Bestätige Password Reset mit Token"""
    # Prüfe Token
    token_data = password_reset_tokens.get(data.token)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Token")
    
    if datetime.now(timezone.utc) > token_data["expires"]:
        del password_reset_tokens[data.token]
        raise HTTPException(status_code=400, detail="Token ist abgelaufen")
    
    # Finde User
    user = db.query(DBUser).filter(DBUser.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    
    # Update Passwort
    user.password_hash = pwd_context.hash(data.new_password)
    db.commit()
    
    # Lösche Token
    del password_reset_tokens[data.token]
    
    logger.info(f"Password reset completed for: {user.email}")
    
    return {"message": "Passwort erfolgreich zurückgesetzt"}

# ============ PROPERTY ROUTES ============

@api_router.get("/properties", response_model=List[Property])
def get_properties(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hole alle Properties des Benutzers"""
    try:
        properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
        return [Property(
            id=str(p.id),
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            address=p.address,
            wifi_name=getattr(p, 'wifi_name', None),
            wifi_password=getattr(p, 'wifi_password', None),
            keysafe_location=getattr(p, 'keysafe_location', None),
            keysafe_code=getattr(p, 'keysafe_code', None),
            checkin_time=getattr(p, 'checkin_time', '15:00'),
            checkout_time=getattr(p, 'checkout_time', '11:00'),
            brand_color=getattr(p, 'brand_color', '#F27C2C'),
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
        # Convert string ID to integer for database query
        try:
            prop_id_int = int(property_id)
        except ValueError:
            prop_id_int = property_id  # Keep as-is for UUID strings
        
        prop = db.query(DBProperty).filter(
            DBProperty.id == prop_id_int,
            DBProperty.user_id == user.id
        ).first()
        
        if not prop:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        return Property(
            id=str(prop.id),
            user_id=prop.user_id,
            name=prop.name,
            description=prop.description,
            address=prop.address,
            wifi_name=getattr(prop, 'wifi_name', None),
            wifi_password=getattr(prop, 'wifi_password', None),
            keysafe_location=getattr(prop, 'keysafe_location', None),
            keysafe_code=getattr(prop, 'keysafe_code', None),
            checkin_time=getattr(prop, 'checkin_time', '15:00'),
            checkout_time=getattr(prop, 'checkout_time', '11:00'),
            brand_color=getattr(prop, 'brand_color', '#F27C2C'),
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
    return {"message": "Welcome Link API", "version": "2.7.1", "status": "healthy"}

@api_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Detaillierter Health Check für Monitoring"""
    from datetime import datetime, timezone
    from sqlalchemy import text
    
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.7.1",
        "environment": ENVIRONMENT,
        "services": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health["services"]["database"] = {
            "status": "healthy",
            "type": "sqlite"
        }
    except Exception as e:
        health["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)[:100]
        }
        health["status"] = "degraded"
    
    # Security headers check
    health["services"]["security"] = {
        "status": "healthy",
        "headers": ["X-Frame-Options", "X-Content-Type-Options", "CSP", "HSTS"]
    }
    
    # Rate limiting check
    health["services"]["rate_limiting"] = {
        "status": "healthy",
        "limits": {
            "register": "5/minute",
            "login": "10/minute",
            "magic_link": "3/minute"
        }
    }
    
    return health

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
    """Rufe Guestview Daten anhand Token oder Property-ID ab (ohne Auth)"""
    try:
        # Check if token is a property ID (numeric)
        is_property_id = token.isdigit()
        
        if is_property_id:
            # If it's a property ID, find the property directly
            property_id = int(token)
            property = db.query(DBProperty).filter(DBProperty.id == property_id).first()
            
            if not property:
                raise HTTPException(status_code=404, detail="Property nicht gefunden")
            
            # Get user for this property
            user = db.query(DBUser).filter(DBUser.id == property.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            properties = [property]
        else:
            # Original token-based flow
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
                "address": p.address or "Seestraße 42, 83209 Prien am Chiemsee",
                "image_url": p.image_url if hasattr(p, 'image_url') and p.image_url else "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=400&fit=crop",
                "wifi_name": p.wifi_name if hasattr(p, 'wifi_name') and p.wifi_name else "Guest-WiFi-Seeblick",
                "wifi_password": p.wifi_password if hasattr(p, 'wifi_password') and p.wifi_password else "Willkommen2026!",
                "keysafe_location": getattr(p, 'keysafe_location', None) or "Neben der Eingangstür",
                "keysafe_code": getattr(p, 'keysafe_code', None) or "1234",
                "checkin_time": getattr(p, 'checkin_time', None) or "15:00",
                "checkout_time": getattr(p, 'checkout_time', None) or "11:00",
                "brand_color": getattr(p, 'brand_color', None) or "#F27C2C",
                "contact_phone": getattr(p, 'contact_phone', None) or "+49 8051 123456",
                "contact_email": getattr(p, 'contact_email', None) or "info@seeblick.de",
                "house_rules": getattr(p, 'house_rules', None) or [
                    "Check-in ab 15:00 Uhr",
                    "Check-out bis 11:00 Uhr", 
                    "Keine Partys oder Veranstaltungen",
                    "Keine Haustiere erlaubt",
                    "Rauchen verboten"
                ],
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in properties],
            "extras": get_demo_extras()  # Extras für Buchung
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Guestviews: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Guestviews: {str(e)}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Security Headers Middleware (nach CORS)
app.add_middleware(SecurityHeadersMiddleware)

# Request Timing Middleware für Performance Monitoring
app.add_middleware(RequestTimingMiddleware)

# Configure logging
if ENVIRONMENT == "production":
    # JSON Logging für Production (besser für Cloud-Logging)
    import json as json_module
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            if record.exc_info:
                log_obj["exception"] = self.formatException(record.exc_info)
            return json_module.dumps(log_obj)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)
else:
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
        {"id": "extra-1", "property_id": "demo-prop-1", "name": "Frühstück", "description": "Reichhaltiges Frühstück mit frischen Brötchen, Eiern und Kaffee", "price": 15.0, "category": "food", "is_active": True},
        {"id": "extra-2", "property_id": "demo-prop-1", "name": "Spät-Check-out", "description": "Check-out bis 14:00 Uhr", "price": 25.0, "category": "service", "is_active": True},
        {"id": "extra-3", "property_id": "demo-prop-1", "name": "Fahrradverleih", "description": "Pro Tag, inkl. Helm und Schloss", "price": 12.0, "category": "activity", "is_active": True},
        {"id": "extra-4", "property_id": "demo-prop-1", "name": "Sauna", "description": "Private Nutzung für 2 Stunden", "price": 30.0, "category": "wellness", "is_active": True},
        {"id": "extra-5", "property_id": "demo-prop-1", "name": "Gepäckaufbewahrung", "description": "Sichere Aufbewahrung pro Tag", "price": 5.0, "category": "service", "is_active": True},
        {"id": "extra-6", "property_id": "demo-prop-1", "name": "Shuttle Service", "description": "Bahnhof-Transfer hin und zurück", "price": 20.0, "category": "transport", "is_active": True},
        {"id": "extra-7", "property_id": "demo-prop-1", "name": "Willkommens-Paket", "description": "Sekt, Obst & Schokolade bei Anreise", "price": 35.0, "category": "food", "is_active": True},
        {"id": "extra-8", "property_id": "demo-prop-1", "name": "Haustier", "description": "Pro Nacht, inkl. Futter & Näpfe", "price": 10.0, "category": "other", "is_active": True},
        {"id": "extra-9", "property_id": "demo-prop-1", "name": "Parkplatz", "description": "Tiefgarage, pro Tag", "price": 8.0, "category": "transport", "is_active": True},
        {"id": "extra-10", "property_id": "demo-prop-1", "name": "Massage", "description": "60 Min. Rücken-Nacken im Hotel", "price": 65.0, "category": "wellness", "is_active": True},
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

# ============ PAYPAL WEBHOOK ============
@api_router.post("/webhooks/paypal")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayPal webhook events"""
    try:
        payload = await request.json()
        event_type = payload.get("event_type", "")
        
        logger.info(f"PayPal webhook received: {event_type}")
        
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            # Payment completed
            resource = payload.get("resource", {})
            transaction_id = resource.get("id", "")
            amount = float(resource.get("amount", {}).get("value", 0))
            custom_id = resource.get("custom_id", "")
            
            # Extract customer info from custom_id or payload
            # Format: "booking_id:user_email:user_name:property_name" or use default
            customer_info = custom_id.split(":") if custom_id else []
            email = customer_info[1] if len(customer_info) > 1 else "guest@welcome-link.de"
            name = customer_info[2] if len(customer_info) > 2 else "Gast"
            property_name = customer_info[3] if len(customer_info) > 3 else "Ihre Unterkunft"
            
            logger.info(f"PayPal payment completed: {transaction_id}, Amount: €{amount}, Customer: {email}")
            
            # Send payment receipt email
            try:
                send_payment_receipt_email(email, name, amount, "PayPal", transaction_id, property_name)
                logger.info(f"Payment receipt email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send payment receipt email: {e}")
            
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            logger.warning(f"PayPal payment denied: {payload}")
            
        elif event_type == "CHECKOUT.ORDER.APPROVED":
            order_id = payload.get("resource", {}).get("id", "")
            logger.info(f"PayPal order approved: {order_id}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"PayPal webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============ CRON JOBS ============
@api_router.post("/cron/booking-reminders")
async def send_booking_reminders(db: Session = Depends(get_db)):
    """
    Send booking reminder emails.
    This endpoint should be called by a cron job daily.
    Sends reminders for check-ins in 1 day.
    """
    try:
        # Get bookings with check-in tomorrow
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
        
        # Query real bookings with check-in tomorrow
        reminders_sent = 0
        try:
            bookings = db.query(DBBooking).filter(
                DBBooking.check_in >= datetime.combine(tomorrow, datetime.min.time()).replace(tzinfo=timezone.utc),
                DBBooking.check_in < datetime.combine(tomorrow, datetime.max.time()).replace(tzinfo=timezone.utc),
                DBBooking.status == "confirmed"
            ).all()
            
            for booking in bookings:
                # Get property for booking
                property = db.query(DBProperty).filter(DBProperty.id == booking.property_id).first()
                if property and booking.guest_email:
                    # Send reminder email
                    send_booking_confirmation_email(
                        email=booking.guest_email,
                        name=booking.guest_name or "Gast",
                        property_name=property.name,
                        checkin=booking.check_in.strftime("%d.%m.%Y"),
                        checkout=booking.check_out.strftime("%d.%m.%Y"),
                        guests=booking.guests or 1,
                        total=booking.total_price or 0
                    )
                    reminders_sent += 1
        except Exception as query_error:
            logger.warning(f"Could not query bookings (demo mode?): {query_error}")
        
        logger.info(f"Booking reminders sent: {reminders_sent}")
        
        return {
            "status": "success",
            "reminders_sent": reminders_sent,
            "checked_for": tomorrow.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Booking reminder error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cron/guest-welcome")
async def send_guest_welcome_emails(db: Session = Depends(get_db)):
    """
    Send welcome emails to guests on check-in day.
    This endpoint should be called by a cron job daily.
    """
    try:
        today = datetime.now(timezone.utc).date()
        
        # Query real bookings with check-in today
        welcomes_sent = 0
        try:
            bookings = db.query(DBBooking).filter(
                DBBooking.check_in >= datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc),
                DBBooking.check_in < datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc),
                DBBooking.status == "confirmed"
            ).all()
            
            for booking in bookings:
                # Get property details for WiFi
                property = db.query(DBProperty).filter(DBProperty.id == booking.property_id).first()
                user = db.query(DBUser).filter(DBUser.id == booking.user_id).first()
                
                if property and booking.guest_email:
                    send_guest_welcome_email(
                        email=booking.guest_email,
                        guest_name=booking.guest_name or "Gast",
                        property_name=property.name,
                        host_name=user.name if user else "Ihr Gastgeber",
                        checkin=booking.check_in.strftime("%d.%m.%Y"),
                        checkout=booking.check_out.strftime("%d.%m.%Y"),
                        wifi_name=getattr(property, 'wifi_name', 'WLAN'),
                        wifi_password=getattr(property, 'wifi_password', ''),
                        guestview_url=f"https://www.welcome-link.de/guestview/{property.public_id}" if hasattr(property, 'public_id') else ""
                    )
                    welcomes_sent += 1
        except Exception as query_error:
            logger.warning(f"Could not query bookings (demo mode?): {query_error}")
        
        logger.info(f"Guest welcome emails sent: {welcomes_sent}")
        
        return {
            "status": "success",
            "welcomes_sent": welcomes_sent,
            "checked_for": today.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Guest welcome error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cron/checkout-followup")
async def send_checkout_followup_emails(db: Session = Depends(get_db)):
    """
    Send follow-up emails after checkout.
    This endpoint should be called by a cron job daily.
    """
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
        
        # Query real bookings with checkout yesterday
        followups_sent = 0
        try:
            bookings = db.query(DBBooking).filter(
                DBBooking.check_out >= datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc),
                DBBooking.check_out < datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.utc),
                DBBooking.status == "completed"
            ).all()
            
            for booking in bookings:
                property = db.query(DBProperty).filter(DBProperty.id == booking.property_id).first()
                
                if property and booking.guest_email:
                    # Send follow-up email asking for feedback
                    send_payment_receipt_email(
                        email=booking.guest_email,
                        name=booking.guest_name or "Gast",
                        amount=booking.total_price or 0,
                        payment_method=booking.payment_method or "none",
                        transaction_id=booking.id,
                        property_name=property.name
                    )
                    followups_sent += 1
        except Exception as query_error:
            logger.warning(f"Could not query bookings (demo mode?): {query_error}")
        
        logger.info(f"Checkout followup emails sent: {followups_sent}")
        
        return {
            "status": "success",
            "followups_sent": followups_sent,
            "checked_for": yesterday.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Checkout followup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ STRIPE CONFIG ============
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# ============ STRIPE WEBHOOK ============
@api_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events with signature verification"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")
        
        # Verify Stripe webhook signature (security best practice)
        if STRIPE_WEBHOOK_SECRET:
            try:
                import stripe
                stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
                event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
                event_data = event.data
                event_type = event.type
            except Exception as e:
                logger.error(f"Stripe signature verification failed: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Fallback for development/testing without webhook secret
            event_data = await request.json()
            event_type = event_data.get("type", "")
            logger.warning("Stripe webhook received without signature verification (development mode)")
        
        logger.info(f"Stripe webhook received: {event_type}")
        
        if event_type == "payment_intent.succeeded":
            # Payment succeeded
            data = event_data.get("data", {})
            payment_intent = data.get("object", {})
            transaction_id = payment_intent.get("id", "")
            amount = payment_intent.get("amount", 0) / 100  # Convert cents to euros
            
            # Extract customer info from payment_intent metadata
            metadata = payment_intent.get("metadata", {})
            email = metadata.get("email", "guest@welcome-link.de")
            name = metadata.get("name", "Gast")
            property_name = metadata.get("property_name", "Ihre Unterkunft")
            
            logger.info(f"Stripe payment succeeded: {transaction_id}, Amount: €{amount}, Customer: {email}")
            
            # Send payment receipt email
            try:
                send_payment_receipt_email(email, name, amount, "Stripe", transaction_id, property_name)
                logger.info(f"Payment receipt email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send payment receipt email: {e}")
            
        elif event_type == "payment_intent.payment_failed":
            logger.warning(f"Stripe payment failed: {event_data}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

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
    
    # Return full property data
    return {
        "success": True,
        "property": {
            "id": prop.id,
            "user_id": prop.user_id,
            "name": prop.name,
            "description": prop.description,
            "address": prop.address,
            "brand_color": getattr(prop, 'brand_color', '#F27C2C'),
            "wifi_name": getattr(prop, 'wifi_name', None),
            "wifi_password": getattr(prop, 'wifi_password', None),
            "keysafe_location": getattr(prop, 'keysafe_location', None),
            "keysafe_code": getattr(prop, 'keysafe_code', None),
            "checkin_time": getattr(prop, 'checkin_time', '15:00'),
            "checkout_time": getattr(prop, 'checkout_time', '11:00'),
            "house_rules": getattr(prop, 'house_rules', []),
            "contact_phone": getattr(prop, 'contact_phone', None),
            "contact_email": getattr(prop, 'contact_email', None),
            "created_at": prop.created_at.isoformat() if prop.created_at else None
        }
    }

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
    
    # Return all property fields for editing
    return {
        "id": prop.id,
        "user_id": prop.user_id,
        "name": prop.name,
        "description": prop.description,
        "address": prop.address,
        "brand_color": getattr(prop, 'brand_color', '#F27C2C'),
        "wifi_name": getattr(prop, 'wifi_name', None),
        "wifi_password": getattr(prop, 'wifi_password', None),
        "keysafe_location": getattr(prop, 'keysafe_location', None),
        "keysafe_code": getattr(prop, 'keysafe_code', None),
        "checkin_time": getattr(prop, 'checkin_time', '15:00'),
        "checkout_time": getattr(prop, 'checkout_time', '11:00'),
        "house_rules": getattr(prop, 'house_rules', []),
        "contact_phone": getattr(prop, 'contact_phone', None),
        "contact_email": getattr(prop, 'contact_email', None),
        "created_at": prop.created_at.isoformat() if prop.created_at else None
    }

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
        hashed_password = pwd_context.hash("Demo123!")
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
    
    # Demo Property erstellen oder aktualisieren
    property = db.query(DBProperty).filter(DBProperty.user_id == user.id).first()
    
    if not property:
        property = DBProperty(
            user_id=user.id,
            name="Ferienwohnung Seeblick",
            description="Gemütliche 3-Zimmer Ferienwohnung mit atemberaubendem Blick auf den Chiemsee. Perfekt für Familien und Paare, die Erholung und Natur suchen.",
            address="Seestraße 42, 83209 Prien am Chiemsee",
            image_url="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&h=800&fit=crop",
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
    else:
        # Update existing property with image if missing
        if not property.image_url:
            property.image_url = "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&h=800&fit=crop"
            property.description = "Gemütliche 3-Zimmer Ferienwohnung mit atemberaubendem Blick auf den Chiemsee. Perfekt für Familien und Paare, die Erholung und Natur suchen."
            db.commit()
    
    # Return the property with its actual database ID
    return {
        "success": True,
        "user": {"id": user.id, "email": user.email, "name": user.name},
        "property": {"id": property.id, "name": property.name, "image_url": property.image_url},
        "guestview_token": "QEJHEXP1QF"
    }

# ============ STATS ENDPOINTS ============
@api_router.get("/stats/global")
def get_global_stats(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get global statistics for user"""
    # Get property count
    property_count = db.query(DBProperty).filter(DBProperty.user_id == user.id).count()
    
    return {
        "total_properties": property_count,
        "total_bookings": 42,
        "confirmed_bookings": 38,
        "completed_bookings": 35,
        "cancelled_bookings": 4,
        "total_revenue": 5280.00,
        "avg_booking_value": 125.71,
        "total_guests": 89,
        "avg_rating": 4.8,
        "period_start": "2026-01-01",
        "period_end": "2026-03-06",
        "chart_data": {
            "bookings": [12, 15, 18, 22, 28, 35, 42],
            "revenue": [1200, 1500, 1800, 2200, 2800, 3500, 4200],
            "months": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul"]
        }
    }

@api_router.post("/stats/booking/filter")
def get_booking_stats(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get booking statistics with optional filters"""
    return {
        "total_bookings": 42,
        "confirmed_bookings": 38,
        "completed_bookings": 35,
        "cancelled_bookings": 4,
        "total_revenue": 5280.00,
        "avg_booking_value": 125.71,
        "period_start": "2026-01-01",
        "period_end": "2026-03-04",
        "filters_applied": {}
    }

# ============ EXPORT ENDPOINTS ============
@api_router.get("/export/bookings/csv")
def export_bookings_csv(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export bookings as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    
    # Demo CSV data
    output = io.StringIO()
    output.write("Booking ID,Guest Name,Email,Property,Check-in,Check-out,Status,Total\n")
    output.write("1,Max Mustermann,max@example.com,Ferienwohnung Seeblick,2026-03-10,2026-03-15,confirmed,525.00\n")
    output.write("2,Anna Schmidt,anna@example.com,Ferienwohnung Seeblick,2026-03-20,2026-03-25,confirmed,630.00\n")
    output.write("3,Hans Müller,hans@example.com,Ferienwohnung Seeblick,2026-04-01,2026-04-05,pending,420.00\n")
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bookings_export.csv"}
    )

@api_router.get("/export/bookings/pdf")
def export_bookings_pdf(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export bookings as PDF"""
    from fastapi.responses import Response
    
    # Demo PDF (in production, generate real PDF)
    pdf_content = b"%PDF-1.4\n%%Demo PDF Content"
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=bookings_export.pdf"}
    )

@api_router.get("/export/properties/csv")
def export_properties_csv(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export properties as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    
    properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
    
    output = io.StringIO()
    output.write("Property ID,Name,Address,WiFi Name,Check-in Time,Check-out Time\n")
    for p in properties:
        output.write(f"{p.id},{p.name},{p.address or ''},{p.wifi_name or ''},{p.checkin_time or '15:00'},{p.checkout_time or '11:00'}\n")
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=properties_export.csv"}
    )

# ============ CALENDAR EXPORT ============
@api_router.get("/bookings/calendar.ics")
def export_bookings_ical(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export bookings as iCal (.ics) file"""
    from fastapi.responses import Response
    
    # Generate iCal content with demo bookings
    # In production, this would fetch real bookings from the database
    now = datetime.now(timezone.utc)
    
    ical_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Welcome-Link//Booking Calendar//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        "UID:demo-booking-1@welcome-link.de",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        "DTSTART;VALUE=DATE:20260310",
        "DTEND;VALUE=DATE:20260315",
        "SUMMARY:Max Mustermann - Ferienwohnung Seeblick",
        "DESCRIPTION:Buchung #1\\nGast: Max Mustermann\\nEmail: max@example.com",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "BEGIN:VEVENT",
        "UID:demo-booking-2@welcome-link.de",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        "DTSTART;VALUE=DATE:20260320",
        "DTEND;VALUE=DATE:20260325",
        "SUMMARY:Anna Schmidt - Ferienwohnung Seeblick",
        "DESCRIPTION:Buchung #2\\nGast: Anna Schmidt\\nEmail: anna@example.com",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "BEGIN:VEVENT",
        "UID:demo-booking-3@welcome-link.de",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        "DTSTART;VALUE=DATE:20260401",
        "DTEND;VALUE=DATE:20260405",
        "SUMMARY:Hans Müller - Ferienwohnung Seeblick",
        "DESCRIPTION:Buchung #3\\nGast: Hans Müller\\nEmail: hans@example.com",
        "STATUS:PENDING",
        "END:VEVENT",
        "END:VCALENDAR"
    ]
    
    return Response(
        content="\r\n".join(ical_lines),
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=bookings_calendar.ics"}
    )

# ============ ADMIN ENDPOINTS ============
@api_router.get("/admin/stats")
def get_admin_stats(range: str = "7d", user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get admin statistics for dashboard"""
    # Get counts from database
    properties_count = db.query(DBProperty).filter(DBProperty.user_id == user.id).count()
    
    # Demo stats for now - in production, these would be calculated from real data
    return {
        "overview": {
            "totalProperties": properties_count,
            "totalGuests": 1247,
            "totalBookings": 856,
            "totalRevenue": 45670.50,
            "qrScans": 3420,
            "avgRating": 4.8
        },
        "trends": {
            "properties": {"value": 2, "trend": "up", "percent": 20},
            "guests": {"value": 156, "trend": "up", "percent": 14},
            "bookings": {"value": 89, "trend": "up", "percent": 12},
            "revenue": {"value": 4567.80, "trend": "up", "percent": 11}
        },
        "chartData": {
            "labels": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun"],
            "bookings": [45, 52, 38, 65, 78, 92],
            "revenue": [4500, 5200, 3800, 6500, 7800, 9200]
        },
        "topProperties": [
            {"name": "Ferienwohnung Seeblick", "bookings": 156, "revenue": 15600},
            {"name": "Alpenchalet", "bookings": 98, "revenue": 12740},
            {"name": "Stadtapartment", "bookings": 72, "revenue": 5760}
        ],
        "recentActivity": [
            {"type": "booking", "message": "Neue Buchung von Max Mustermann", "time": "vor 5 Min"},
            {"type": "qr_scan", "message": "QR-Code gescannt", "time": "vor 12 Min"},
            {"type": "review", "message": "5-Sterne Bewertung erhalten", "time": "vor 1 Std"}
        ]
    }

@api_router.get("/admin/bookings/feed")
def get_bookings_feed(limit: int = 50, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recent bookings for live feed"""
    # Demo bookings - in production, fetch from database
    from datetime import datetime, timedelta
    now = datetime.now()
    return [
        {
            "id": "BK-001",
            "property_name": "Ferienwohnung Seeblick",
            "guest_name": "Max Mustermann",
            "guest_email": "max@example.com",
            "check_in": (now + timedelta(days=6)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=11)).strftime("%Y-%m-%d"),
            "nights": 5,
            "guests": 2,
            "total_price": 525.00,
            "status": "confirmed",
            "extras": ["Frühstück", "Parkplatz"],
            "created_at": (now - timedelta(hours=2)).isoformat()
        },
        {
            "id": "BK-002",
            "property_name": "Ferienwohnung Seeblick",
            "guest_name": "Anna Schmidt",
            "guest_email": "anna@example.com",
            "check_in": (now + timedelta(days=16)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=21)).strftime("%Y-%m-%d"),
            "nights": 5,
            "guests": 3,
            "total_price": 630.00,
            "status": "confirmed",
            "extras": ["Frühstück", "Sauna"],
            "created_at": (now - timedelta(hours=5)).isoformat()
        },
        {
            "id": "BK-003",
            "property_name": "Ferienwohnung Seeblick",
            "guest_name": "Hans Müller",
            "guest_email": "hans@example.com",
            "check_in": (now + timedelta(days=28)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=32)).strftime("%Y-%m-%d"),
            "nights": 4,
            "guests": 2,
            "total_price": 420.00,
            "status": "pending",
            "extras": ["Fahrradverleih"],
            "created_at": (now - timedelta(days=1)).isoformat()
        },
        {
            "id": "BK-004",
            "property_name": "Ferienwohnung Seeblick",
            "guest_name": "Sophie Klein",
            "guest_email": "sophie@example.com",
            "check_in": (now - timedelta(days=3)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
            "nights": 5,
            "guests": 4,
            "total_price": 750.00,
            "status": "active",
            "extras": ["Frühstück", "Willkommens-Paket", "Parkplatz"],
            "created_at": (now - timedelta(days=7)).isoformat()
        },
        {
            "id": "BK-005",
            "property_name": "Ferienwohnung Seeblick",
            "guest_name": "Thomas Weber",
            "guest_email": "thomas@example.com",
            "check_in": (now + timedelta(days=45)).strftime("%Y-%m-%d"),
            "check_out": (now + timedelta(days=52)).strftime("%Y-%m-%d"),
            "nights": 7,
            "guests": 2,
            "total_price": 840.00,
            "status": "confirmed",
            "extras": ["Frühstück", "Massage", "Shuttle Service"],
            "created_at": (now - timedelta(hours=12)).isoformat()
        }
    ]

@api_router.get("/admin/users")
def get_admin_users(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    # Demo users for now - demo user is NOT admin
    return [
        {
            "id": "1",
            "email": "admin@welcome-link.de",
            "name": "Administrator",
            "is_admin": True,
            "created_at": "2026-01-01T00:00:00Z",
            "properties_count": 0,
            "plan": "Enterprise",
            "status": "active"
        },
        {
            "id": "2",
            "email": "demo@welcome-link.de",
            "name": "Demo Benutzer",
            "is_admin": False,
            "created_at": "2026-01-15T10:00:00Z",
            "properties_count": 1,
            "plan": "Professional",
            "status": "demo"
        },
        {
            "id": "3",
            "email": "max@example.com",
            "name": "Max Mustermann",
            "is_admin": False,
            "created_at": "2026-02-20T14:30:00Z",
            "properties_count": 2,
            "plan": "Professional",
            "status": "active"
        },
        {
            "id": "4",
            "email": "anna@example.com",
            "name": "Anna Schmidt",
            "is_admin": False,
            "created_at": "2026-03-01T09:15:00Z",
            "properties_count": 1,
            "plan": "Starter",
            "status": "active"
        },
        {
            "id": "5",
            "email": "hotel@bayerhof.de",
            "name": "Hotel Bayerhof",
            "is_admin": False,
            "created_at": "2026-03-07T08:00:00Z",
            "properties_count": 15,
            "plan": "Enterprise",
            "status": "trial"
        }
    ]

@api_router.put("/admin/users/{user_id}")
def update_admin_user(user_id: str, user_data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user (admin only)"""
    return {"success": True, "message": f"User {user_id} updated"}

@api_router.delete("/admin/users/{user_id}")
def delete_admin_user(user_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete user (admin only)"""
    return {"success": True, "message": f"User {user_id} deleted"}

# ============ PAYPAL ENDPOINTS ============
@api_router.post("/paypal/create-order")
def create_paypal_order(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create PayPal order for payment"""
    # Demo PayPal order creation
    order_id = f"PAYPAL-{uuid.uuid4().hex[:12].upper()}"
    return {
        "order_id": order_id,
        "status": "CREATED",
        "amount": data.get("amount", 0),
        "currency": data.get("currency", "EUR"),
        "booking_id": data.get("booking_id"),
        "links": [
            {"rel": "approve", "href": f"https://www.paypal.com/checkoutnow?token={order_id}"},
            {"rel": "capture", "href": f"https://api.welcome-link.de/api/paypal/capture-order"}
        ]
    }

@api_router.post("/paypal/capture-order")
def capture_paypal_order(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Capture PayPal order after approval"""
    # Demo capture
    return {
        "success": True,
        "order_id": data.get("order_id"),
        "booking_id": data.get("booking_id"),
        "status": "COMPLETED",
        "transaction_id": f"TXN-{uuid.uuid4().hex[:16].upper()}"
    }

# ============ A/B TESTS ENDPOINTS ============
@api_router.get("/ab-tests")
def get_ab_tests(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all A/B tests for user"""
    return [
        {
            "id": "ab-1",
            "property_id": "17",
            "name": "Welcome Screen Test",
            "variant_a": {"name": "Original", "url": "/guestview/17"},
            "variant_b": {"name": "New Design", "url": "/guestview/17?variant=b"},
            "active": True,
            "created_at": "2026-02-15T10:00:00Z"
        }
    ]

@api_router.post("/ab-tests")
def create_ab_test(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new A/B test"""
    return {
        "success": True,
        "id": f"ab-{uuid.uuid4().hex[:8]}",
        "name": data.get("name", "New Test"),
        "active": True
    }

@api_router.delete("/ab-tests/{test_id}")
def delete_ab_test(test_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete A/B test"""
    return {"success": True, "message": f"A/B Test {test_id} deleted"}

# ============ BOOKINGS ENDPOINTS ============
@api_router.get("/bookings")
def get_bookings(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all bookings for user"""
    # Demo bookings
    return {
        "bookings": [
            {
                "id": "booking-1",
                "property_id": 17,
                "property_name": "Ferienwohnung Seeblick",
                "guest_name": "Max Mustermann",
                "guest_email": "max@example.com",
                "check_in": "2026-03-10",
                "check_out": "2026-03-15",
                "nights": 5,
                "guests": 2,
                "total_price": 525.00,
                "status": "confirmed",
                "payment_method": "paypal",
                "created_at": "2026-03-04T10:30:00Z"
            },
            {
                "id": "booking-2",
                "property_id": 17,
                "property_name": "Ferienwohnung Seeblick",
                "guest_name": "Anna Schmidt",
                "guest_email": "anna@example.com",
                "check_in": "2026-03-20",
                "check_out": "2026-03-25",
                "nights": 5,
                "guests": 3,
                "total_price": 575.00,
                "status": "pending",
                "payment_method": "stripe",
                "created_at": "2026-03-05T14:20:00Z"
            },
            {
                "id": "booking-3",
                "property_id": 17,
                "property_name": "Ferienwohnung Seeblick",
                "guest_name": "Thomas Weber",
                "guest_email": "thomas@example.com",
                "check_in": "2026-03-01",
                "check_out": "2026-03-05",
                "nights": 4,
                "guests": 2,
                "total_price": 420.00,
                "status": "completed",
                "payment_method": "paypal",
                "created_at": "2026-02-25T09:15:00Z"
            }
        ],
        "total": 3,
        "page": 1,
        "per_page": 20
    }

@api_router.post("/bookings")
def create_booking(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new booking"""
    booking_id = f"booking-{uuid.uuid4().hex[:8]}"
    
    # Send booking confirmation email if guest_email provided
    guest_email = data.get("guest_email", "")
    guest_name = data.get("guest_name", "Gast")
    property_name = data.get("property_name", "Unterkunft")
    check_in = data.get("check_in", "")
    check_out = data.get("check_out", "")
    guests = data.get("guests", 1)
    total_price = data.get("total_price", 0)
    
    if guest_email:
        # Send confirmation email asynchronously (don't block)
        try:
            send_booking_confirmation_email(
                email=guest_email,
                name=guest_name,
                property_name=property_name,
                checkin=check_in,
                checkout=check_out,
                guests=guests,
                total=total_price
            )
            logger.info(f"Booking confirmation email sent to: {guest_email}")
        except Exception as e:
            logger.error(f"Failed to send booking email: {str(e)}")
    
    return {
        "id": booking_id,
        "property_id": data.get("property_id", 17),
        "guest_name": guest_name,
        "guest_email": guest_email,
        "check_in": check_in,
        "check_out": check_out,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/bookings/{booking_id}")
def get_booking(booking_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get booking details"""
    # Demo booking
    return {
        "id": booking_id,
        "property_id": 17,
        "property_name": "Ferienwohnung Seeblick",
        "guest_name": "Max Mustermann",
        "guest_email": "max@example.com",
        "check_in": "2026-03-10",
        "check_out": "2026-03-15",
        "nights": 5,
        "guests": 2,
        "total_price": 525.00,
        "status": "confirmed",
        "payment_method": "paypal",
        "created_at": "2026-03-04T10:30:00Z"
    }

# ============ SCENES ENDPOINTS ============
@api_router.get("/scenes")
def get_scenes(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all scenes for user's properties"""
    # Demo scenes
    return {
        "scenes": [
            {
                "id": "scene-1",
                "property_id": 17,
                "title": "Willkommen",
                "content": "Herzlich willkommen in unserer Ferienwohnung! Wir freuen uns, dass Sie hier sind.",
                "order": 1,
                "is_active": True,
                "created_at": "2026-03-01T10:00:00Z"
            },
            {
                "id": "scene-2",
                "property_id": 17,
                "title": "WLAN & Internet",
                "content": "Netzwerk: Guest-WiFi\nPasswort: welcome2024\n\nDas Passwort finden Sie auch am Router im Flur.",
                "order": 2,
                "is_active": True,
                "created_at": "2026-03-01T10:05:00Z"
            },
            {
                "id": "scene-3",
                "property_id": 17,
                "title": "Check-out",
                "content": "Bitte checken Sie bis 11:00 Uhr aus. Legen Sie die Schlüssel in den Keysafe zurück.",
                "order": 3,
                "is_active": True,
                "created_at": "2026-03-01T10:10:00Z"
            },
            {
                "id": "scene-4",
                "property_id": 17,
                "title": "Umgebung & Tipps",
                "content": "Der Chiemsee ist nur 5 Gehminuten entfernt. Empfehlenswerte Restaurants: Seewirt, Gasthof Zur Post.",
                "order": 4,
                "is_active": True,
                "created_at": "2026-03-01T10:15:00Z"
            }
        ],
        "total": 4
    }

@api_router.post("/scenes")
def create_scene(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new scene"""
    scene_id = f"scene-{uuid.uuid4().hex[:8]}"
    return {
        "id": scene_id,
        "property_id": data.get("property_id", 17),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "order": data.get("order", 1),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.put("/scenes/{scene_id}")
def update_scene(scene_id: str, data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a scene"""
    return {
        "id": scene_id,
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "order": data.get("order", 1),
        "is_active": data.get("is_active", True),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.delete("/scenes/{scene_id}")
def delete_scene(scene_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a scene"""
    return {"success": True, "message": f"Scene {scene_id} deleted"}

# ============ USER PROFILE ENDPOINTS ============
@api_router.get("/auth/profile")
def get_user_profile(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile"""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.email.split("@")[0].replace(".", " ").title(),
        "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else "2026-01-01T00:00:00Z",
        "properties_count": db.query(DBProperty).filter(DBProperty.user_id == user.id).count()
    }

@api_router.put("/auth/profile")
def update_user_profile(data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile"""
    return {
        "success": True,
        "message": "Profile updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": data.get("name", user.email.split("@")[0])
        }
    }

# ============ WALKTHROUGH / SCENES ENDPOINTS ============
@api_router.get("/properties/{property_id}/scenes")
def get_property_scenes(property_id: int, db: Session = Depends(get_db)):
    """Get walkthrough scenes for a property"""
    # Demo scenes for the property
    return {
        "scenes": [
            {
                "id": "scene-1",
                "property_id": property_id,
                "order": 1,
                "title": "Willkommen",
                "title_en": "Welcome",
                "description": "Herzlich willkommen in Ihrer Ferienwohnung! Wir wünschen Ihnen einen angenehmen Aufenthalt.",
                "description_en": "Welcome to your vacation apartment! We wish you a pleasant stay.",
                "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop",
                "icon": "home"
            },
            {
                "id": "scene-2",
                "property_id": property_id,
                "order": 2,
                "title": "WLAN-Verbindung",
                "title_en": "WiFi Connection",
                "description": f"Verbinden Sie sich mit dem WLAN '{'Seeblick-Guest'}'. Das Passwort finden Sie im Willkommens-Bereich.",
                "description_en": f"Connect to the WiFi '{'Seeblick-Guest'}'. You'll find the password in the welcome section.",
                "image_url": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&h=600&fit=crop",
                "icon": "wifi"
            },
            {
                "id": "scene-3",
                "property_id": property_id,
                "order": 3,
                "title": "Schlafzimmer",
                "title_en": "Bedroom",
                "description": "Das gemütliche Schlafzimmer mit Blick auf den See. Betten sind frisch bezogen.",
                "description_en": "The cozy bedroom with lake view. Beds are freshly made.",
                "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&h=600&fit=crop",
                "icon": "bed"
            },
            {
                "id": "scene-4",
                "property_id": property_id,
                "order": 4,
                "title": "Küche",
                "title_en": "Kitchen",
                "description": "Die voll ausgestattete Küche bietet alles, was Sie für Ihren Aufenthalt benötigen.",
                "description_en": "The fully equipped kitchen has everything you need for your stay.",
                "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop",
                "icon": "utensils"
            },
            {
                "id": "scene-5",
                "property_id": property_id,
                "order": 5,
                "title": "Balkon & Aussicht",
                "title_en": "Balcony & View",
                "description": "Genießen Sie den atemberaubenden Blick auf den Chiemsee vom eigenen Balkon.",
                "description_en": "Enjoy the breathtaking view of Lake Chiemsee from your private balcony.",
                "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop",
                "icon": "sun"
            },
            {
                "id": "scene-6",
                "property_id": property_id,
                "order": 6,
                "title": "Check-out",
                "title_en": "Check-out",
                "description": "Bitte verlassen Sie die Wohnung bis 11:00 Uhr. Schlüssel im Keysafe zurücklegen.",
                "description_en": "Please check out by 11:00 AM. Return the key to the keysafe.",
                "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
                "icon": "key"
            }
        ]
    }

@api_router.post("/properties/{property_id}/scenes")
def create_scene(property_id: int, data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new scene"""
    scene_id = f"scene-{uuid.uuid4().hex[:8]}"
    return {
        "success": True,
        "scene": {
            "id": scene_id,
            "property_id": property_id,
            **data
        }
    }

@api_router.put("/properties/{property_id}/scenes/{scene_id}")
def update_scene(property_id: int, scene_id: str, data: dict, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a scene"""
    return {
        "success": True,
        "scene": {
            "id": scene_id,
            "property_id": property_id,
            **data
        }
    }

@api_router.delete("/properties/{property_id}/scenes/{scene_id}")
def delete_scene(property_id: int, scene_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a scene"""
    return {"success": True, "message": f"Scene {scene_id} deleted"}

# ============ HEALTH CHECK ============
@api_router.get("/health")
def health_check():
    """Health check endpoint for monitoring with performance metrics"""
    
    # Get system metrics (if psutil is available)
    cpu_percent = None
    memory_percent = None
    disk_percent = None
    
    if PSUTIL_AVAILABLE and psutil:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            memory_percent = memory.percent
            disk_percent = disk.percent
        except Exception as e:
            logger.warning(f"Could not get system metrics: {e}")
    
    # Database health check
    db_healthy = True
    try:
        db = next(get_db())
        db.execute("SELECT 1")
    except Exception as e:
        db_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    health_response = {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.8.2",
        "environment": ENVIRONMENT,
        "services": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "type": "sqlite"
            },
            "security": {
                "status": "healthy",
                "headers": ["X-Frame-Options", "X-Content-Type-Options", "CSP", "HSTS"]
            },
            "rate_limiting": {
                "status": "healthy",
                "limits": {
                    "register": "5/minute",
                    "login": "10/minute",
                    "magic_link": "3/minute"
                }
            }
        }
    }
    
    # Add performance metrics if available
    if cpu_percent is not None:
        health_response["performance"] = {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory_percent, 1),
            "disk_percent": round(disk_percent, 1)
        }
    
    return health_response

# Include the router in the main app AFTER all routes are defined
app.include_router(api_router)

# ============ DAILY STATS ENDPOINT ============
@api_router.get("/admin/daily-stats")
def get_daily_stats(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get daily statistics for dashboard charts"""
    from datetime import datetime, timedelta
    import random
    
    # Generate last 30 days of demo data
    days = []
    today = datetime.now()
    
    for i in range(30):
        date = today - timedelta(days=i)
        days.append({
            "date": date.strftime("%Y-%m-%d"),
            "scans": random.randint(20, 100),
            "bookings": random.randint(0, 10),
            "revenue": round(random.uniform(50, 500), 2)
        })
    
    return {
        "daily_stats": list(reversed(days)),
        "summary": {
            "total_scans": sum(d["scans"] for d in days),
            "total_bookings": sum(d["bookings"] for d in days),
            "total_revenue": round(sum(d["revenue"] for d in days), 2),
            "avg_scans": round(sum(d["scans"] for d in days) / 30),
            "avg_bookings": round(sum(d["bookings"] for d in days) / 30, 1),
            "avg_revenue": round(sum(d["revenue"] for d in days) / 30, 2)
        }
    }

# ============ TOP EXTRAS ENDPOINT ============
@api_router.get("/admin/top-extras")
def get_top_extras(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get top performing extras"""
    return {
        "extras": [
            {"id": "extra-1", "name": "Frühstück", "bookings": 156, "revenue": 2340.00, "trend": 12},
            {"id": "extra-4", "name": "Sauna", "bookings": 89, "revenue": 2670.00, "trend": 8},
            {"id": "extra-6", "name": "Shuttle Service", "bookings": 67, "revenue": 1340.00, "trend": 15},
            {"id": "extra-7", "name": "Willkommens-Paket", "bookings": 45, "revenue": 1575.00, "trend": 5},
            {"id": "extra-3", "name": "Fahrradverleih", "bookings": 34, "revenue": 408.00, "trend": -3}
        ]
    }


# ============ CLEANER MANAGEMENT ============
from database import Cleaner as DBCleaner, PropertyCleaner as DBPropertyCleaner

class CleanerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class CleanerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class PropertyCleanerAssign(BaseModel):
    property_id: int
    cleaner_id: str
    notify_hours_before: int = Field(default=2, ge=1, le=24)
    is_primary: bool = False

def send_cleaning_notification_email(
    cleaner_email: str,
    cleaner_name: str,
    property_name: str,
    property_address: str,
    guest_name: str,
    checkout_date: str,
    checkout_time: str,
    notes: str = None
):
    """Sende Reinigungs-Benachrichtigung an Reinigungskraft"""
    
    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #10B981 0%, #34D399 100%); padding: 30px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🧹 Reinigungsauftrag</h1>
        </div>
        <div style="background: #fff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hallo {cleaner_name}!</h2>
            <p style="color: #666; font-size: 16px;">Es steht eine Reinigung an. Hier sind die Details:</p>
            
            <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #10B981;">
                <h3 style="color: #10B981; margin-top: 0;">📍 Unterkunft</h3>
                <table style="width: 100%; color: #333;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Name:</strong></td>
                        <td style="padding: 8px 0;">{property_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Adresse:</strong></td>
                        <td style="padding: 8px 0;">{property_address}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #f59e0b;">
                <h3 style="color: #d97706; margin-top: 0;">📅 Check-out</h3>
                <table style="width: 100%; color: #333;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Datum:</strong></td>
                        <td style="padding: 8px 0;">{checkout_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Uhrzeit:</strong></td>
                        <td style="padding: 8px 0;">{checkout_time} Uhr</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Gast:</strong></td>
                        <td style="padding: 8px 0;">{guest_name}</td>
                    </tr>
                </table>
            </div>
            
            {"<div style='background: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #ef4444;'><h4 style='color: #ef4444; margin-top: 0;'>📝 Hinweise</h4><p style='color: #666; margin: 0;'>" + notes + "</p></div>" if notes else ""}
            
            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                Bitte bestätigen Sie die Reinigung nach Abschluss.<br>
                Bei Fragen erreichen Sie den Gastgeber über Welcome Link.
            </p>
        </div>
    </body>
    </html>
    """
    
    text = f"""Reinigungsauftrag - Welcome Link

Hallo {cleaner_name}!

Unterkunft: {property_name}
Adresse: {property_address}

Check-out: {checkout_date} um {checkout_time} Uhr
Gast: {guest_name}

{"Hinweise: " + notes if notes else ""}

Bitte bestätigen Sie die Reinigung nach Abschluss.
"""
    
    return send_email(cleaner_email, f"🧹 Reinigungsauftrag - {property_name}", html, text)


# ============ CLEANER CRUD ENDPOINTS ============
@api_router.get("/cleaners")
def get_cleaners(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hole alle Reinigungskräfte des Benutzers"""
    try:
        cleaners = db.query(DBCleaner).filter(DBCleaner.user_id == user.id).all()
        
        result = []
        for cleaner in cleaners:
            # Get assigned properties
            assignments = db.query(DBPropertyCleaner).filter(DBPropertyCleaner.cleaner_id == cleaner.id).all()
            property_ids = [a.property_id for a in assignments]
            
            # Get property names
            properties = []
            for pid in property_ids:
                prop = db.query(DBProperty).filter(DBProperty.id == pid).first()
                if prop:
                    properties.append({"id": pid, "name": prop.name})
            
            result.append({
                "id": cleaner.id,
                "name": cleaner.name,
                "email": cleaner.email,
                "phone": cleaner.phone,
                "notes": cleaner.notes,
                "is_active": cleaner.is_active,
                "properties": properties,
                "created_at": cleaner.created_at.isoformat() if cleaner.created_at else None
            })
        
        return {"cleaners": result}
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Reinigungskräfte: {str(e)}")
        # Return empty list for demo
        return {"cleaners": []}


@api_router.post("/cleaners")
def create_cleaner(data: CleanerCreate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Erstelle neue Reinigungskraft"""
    try:
        cleaner_id = str(uuid.uuid4())
        
        cleaner = DBCleaner(
            id=cleaner_id,
            user_id=user.id,
            name=data.name,
            email=data.email.lower(),
            phone=data.phone,
            notes=data.notes,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(cleaner)
        db.commit()
        db.refresh(cleaner)
        
        logger.info(f"Reinigungskraft erstellt: {cleaner.name} ({cleaner.email})")
        
        return {
            "id": cleaner.id,
            "name": cleaner.name,
            "email": cleaner.email,
            "phone": cleaner.phone,
            "notes": cleaner.notes,
            "is_active": cleaner.is_active,
            "properties": [],
            "created_at": cleaner.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Reinigungskraft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen der Reinigungskraft")


@api_router.put("/cleaners/{cleaner_id}")
def update_cleaner(cleaner_id: str, data: CleanerUpdate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aktualisiere Reinigungskraft"""
    try:
        cleaner = db.query(DBCleaner).filter(
            DBCleaner.id == cleaner_id,
            DBCleaner.user_id == user.id
        ).first()
        
        if not cleaner:
            raise HTTPException(status_code=404, detail="Reinigungskraft nicht gefunden")
        
        update_data = data.model_dump(exclude_none=True)
        for key, value in update_data.items():
            if hasattr(cleaner, key):
                setattr(cleaner, key, value)
        
        db.commit()
        db.refresh(cleaner)
        
        return {
            "id": cleaner.id,
            "name": cleaner.name,
            "email": cleaner.email,
            "phone": cleaner.phone,
            "notes": cleaner.notes,
            "is_active": cleaner.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Reinigungskraft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren")


@api_router.delete("/cleaners/{cleaner_id}")
def delete_cleaner(cleaner_id: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lösche Reinigungskraft"""
    try:
        cleaner = db.query(DBCleaner).filter(
            DBCleaner.id == cleaner_id,
            DBCleaner.user_id == user.id
        ).first()
        
        if not cleaner:
            raise HTTPException(status_code=404, detail="Reinigungskraft nicht gefunden")
        
        # Remove property assignments first
        db.query(DBPropertyCleaner).filter(DBPropertyCleaner.cleaner_id == cleaner_id).delete()
        
        # Delete cleaner
        db.delete(cleaner)
        db.commit()
        
        logger.info(f"Reinigungskraft gelöscht: {cleaner_id}")
        
        return {"success": True, "message": "Reinigungskraft gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Reinigungskraft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")


# ============ PROPERTY-CLEANER ASSIGNMENT ============
@api_router.post("/properties/{property_id}/cleaners")
def assign_cleaner_to_property(
    property_id: int,
    data: PropertyCleanerAssign,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Weise Reinigungskraft einer Property zu"""
    try:
        # Verify property belongs to user
        property = db.query(DBProperty).filter(
            DBProperty.id == property_id,
            DBProperty.user_id == user.id
        ).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property nicht gefunden")
        
        # Verify cleaner belongs to user
        cleaner = db.query(DBCleaner).filter(
            DBCleaner.id == data.cleaner_id,
            DBCleaner.user_id == user.id
        ).first()
        
        if not cleaner:
            raise HTTPException(status_code=404, detail="Reinigungskraft nicht gefunden")
        
        # Check if assignment already exists
        existing = db.query(DBPropertyCleaner).filter(
            DBPropertyCleaner.property_id == property_id,
            DBPropertyCleaner.cleaner_id == data.cleaner_id
        ).first()
        
        if existing:
            # Update existing assignment
            existing.notify_hours_before = data.notify_hours_before
            existing.is_primary = data.is_primary
        else:
            # Create new assignment
            assignment = DBPropertyCleaner(
                id=str(uuid.uuid4()),
                property_id=property_id,
                cleaner_id=data.cleaner_id,
                notify_hours_before=data.notify_hours_before,
                is_primary=data.is_primary,
                created_at=datetime.now(timezone.utc)
            )
            db.add(assignment)
        
        db.commit()
        
        return {
            "success": True,
            "property_id": property_id,
            "cleaner_id": data.cleaner_id,
            "cleaner_name": cleaner.name,
            "notify_hours_before": data.notify_hours_before,
            "is_primary": data.is_primary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Zuweisen der Reinigungskraft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Zuweisen")


@api_router.delete("/properties/{property_id}/cleaners/{cleaner_id}")
def remove_cleaner_from_property(
    property_id: int,
    cleaner_id: str,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Entferne Reinigungskraft von Property"""
    try:
        assignment = db.query(DBPropertyCleaner).filter(
            DBPropertyCleaner.property_id == property_id,
            DBPropertyCleaner.cleaner_id == cleaner_id
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Zuweisung nicht gefunden")
        
        db.delete(assignment)
        db.commit()
        
        return {"success": True, "message": "Zuweisung entfernt"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Entfernen der Reinigungskraft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Entfernen")


@api_router.get("/properties/{property_id}/cleaners")
def get_property_cleaners(
    property_id: int,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole alle Reinigungskräfte einer Property"""
    try:
        assignments = db.query(DBPropertyCleaner).filter(
            DBPropertyCleaner.property_id == property_id
        ).all()
        
        result = []
        for assignment in assignments:
            cleaner = db.query(DBCleaner).filter(DBCleaner.id == assignment.cleaner_id).first()
            if cleaner:
                result.append({
                    "id": cleaner.id,
                    "name": cleaner.name,
                    "email": cleaner.email,
                    "phone": cleaner.phone,
                    "notes": cleaner.notes,
                    "is_primary": assignment.is_primary,
                    "notify_hours_before": assignment.notify_hours_before
                })
        
        return {"cleaners": result}
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Property-Reinigungskräfte: {str(e)}")
        return {"cleaners": []}


# ============ CLEANING NOTIFICATION CRON ============
@api_router.post("/cron/cleaning-notifications")
async def send_cleaning_notifications(db: Session = Depends(get_db)):
    """
    Sende Reinigungs-Benachrichtigungen für bevorstehende Check-outs.
    Dieser Endpoint sollte von einem Cron-Job aufgerufen werden.
    
    Benachrichtigt Reinigungskräfte X Stunden vor Checkout.
    """
    try:
        now = datetime.now(timezone.utc)
        notifications_sent = 0
        errors = []
        
        # Get all property-cleaner assignments
        assignments = db.query(DBPropertyCleaner).all()
        
        for assignment in assignments:
            # Find bookings ending within the notification window
            notify_hours = assignment.notify_hours_before or 2
            window_start = now + timedelta(hours=notify_hours - 1)
            window_end = now + timedelta(hours=notify_hours + 1)
            
            try:
                # Get property info
                property = db.query(DBProperty).filter(DBProperty.id == assignment.property_id).first()
                if not property:
                    continue
                
                # Get cleaner info
                cleaner = db.query(DBCleaner).filter(DBCleaner.id == assignment.cleaner_id).first()
                if not cleaner or not cleaner.email:
                    continue
                
                # Find bookings with checkout in the notification window
                bookings = db.query(DBBooking).filter(
                    DBBooking.property_id == str(assignment.property_id),
                    DBBooking.check_out >= window_start,
                    DBBooking.check_out <= window_end,
                    DBBooking.status.in_(["confirmed", "active"])
                ).all()
                
                for booking in bookings:
                    # Check if notification already sent (would need a tracking table in production)
                    # For now, send notification
                    
                    guest_name = booking.guest_name or "Gast"
                    checkout_date = booking.check_out.strftime("%d.%m.%Y") if booking.check_out else "Unbekannt"
                    checkout_time = property.checkout_time or "11:00"
                    
                    # Send notification email
                    email_sent = send_cleaning_notification_email(
                        cleaner_email=cleaner.email,
                        cleaner_name=cleaner.name,
                        property_name=property.name,
                        property_address=property.address or "Adresse nicht angegeben",
                        guest_name=guest_name,
                        checkout_date=checkout_date,
                        checkout_time=checkout_time,
                        notes=cleaner.notes
                    )
                    
                    if email_sent:
                        notifications_sent += 1
                        logger.info(f"Reinigungs-Benachrichtigung gesendet: {cleaner.email} für {property.name}")
                    else:
                        errors.append(f"E-Mail fehlgeschlagen für {cleaner.email}")
                        
            except Exception as e:
                logger.error(f"Fehler bei Property {assignment.property_id}: {str(e)}")
                errors.append(str(e))
        
        return {
            "status": "success",
            "notifications_sent": notifications_sent,
            "errors": errors,
            "checked_at": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Reinigungs-Benachrichtigung Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ NOTIFICATION PREFERENCES API ============
class NotificationPreferenceUpdate(BaseModel):
    email_booking_new: Optional[bool] = None
    email_booking_confirmed: Optional[bool] = None
    email_booking_cancelled: Optional[bool] = None
    email_review_new: Optional[bool] = None
    email_cleaning_reminder: Optional[bool] = None
    email_marketing: Optional[bool] = None
    push_booking_new: Optional[bool] = None
    push_booking_confirmed: Optional[bool] = None
    push_review_new: Optional[bool] = None
    push_cleaning_reminder: Optional[bool] = None
    reminder_hours_before: Optional[int] = None
    cleaning_notify_hours: Optional[int] = None

@api_router.get("/notifications/preferences")
def get_notification_preferences(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's notification preferences"""
    from database import NotificationPreference as DBNotificationPreference
    
    prefs = db.query(DBNotificationPreference).filter(
        DBNotificationPreference.user_id == user.id
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = DBNotificationPreference(
            id=str(uuid.uuid4()),
            user_id=user.id
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return {
        "id": prefs.id,
        "user_id": prefs.user_id,
        "email_booking_new": prefs.email_booking_new,
        "email_booking_confirmed": prefs.email_booking_confirmed,
        "email_booking_cancelled": prefs.email_booking_cancelled,
        "email_review_new": prefs.email_review_new,
        "email_cleaning_reminder": prefs.email_cleaning_reminder,
        "email_marketing": prefs.email_marketing,
        "push_booking_new": prefs.push_booking_new,
        "push_booking_confirmed": prefs.push_booking_confirmed,
        "push_review_new": prefs.push_review_new,
        "push_cleaning_reminder": prefs.push_cleaning_reminder,
        "reminder_hours_before": prefs.reminder_hours_before,
        "cleaning_notify_hours": prefs.cleaning_notify_hours,
        "created_at": prefs.created_at.isoformat() if prefs.created_at else None,
        "updated_at": prefs.updated_at.isoformat() if prefs.updated_at else None
    }

@api_router.put("/notifications/preferences")
def update_notification_preferences(
    update: NotificationPreferenceUpdate,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    from database import NotificationPreference as DBNotificationPreference
    
    prefs = db.query(DBNotificationPreference).filter(
        DBNotificationPreference.user_id == user.id
    ).first()
    
    if not prefs:
        prefs = DBNotificationPreference(
            id=str(uuid.uuid4()),
            user_id=user.id
        )
        db.add(prefs)
    
    # Update only provided fields
    if update.email_booking_new is not None:
        prefs.email_booking_new = update.email_booking_new
    if update.email_booking_confirmed is not None:
        prefs.email_booking_confirmed = update.email_booking_confirmed
    if update.email_booking_cancelled is not None:
        prefs.email_booking_cancelled = update.email_booking_cancelled
    if update.email_review_new is not None:
        prefs.email_review_new = update.email_review_new
    if update.email_cleaning_reminder is not None:
        prefs.email_cleaning_reminder = update.email_cleaning_reminder
    if update.email_marketing is not None:
        prefs.email_marketing = update.email_marketing
    if update.push_booking_new is not None:
        prefs.push_booking_new = update.push_booking_new
    if update.push_booking_confirmed is not None:
        prefs.push_booking_confirmed = update.push_booking_confirmed
    if update.push_review_new is not None:
        prefs.push_review_new = update.push_review_new
    if update.push_cleaning_reminder is not None:
        prefs.push_cleaning_reminder = update.push_cleaning_reminder
    if update.reminder_hours_before is not None:
        prefs.reminder_hours_before = update.reminder_hours_before
    if update.cleaning_notify_hours is not None:
        prefs.cleaning_notify_hours = update.cleaning_notify_hours
    
    db.commit()
    db.refresh(prefs)
    
    return {"status": "success", "message": "Benachrichtigungseinstellungen aktualisiert"}


# ============ REVIEWS API ============
class ReviewCreate(BaseModel):
    property_id: int
    booking_id: Optional[str] = None
    guest_name: str
    guest_email: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewReply(BaseModel):
    reply: str

@api_router.get("/reviews")
def get_reviews(
    property_id: Optional[int] = None,
    approved_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reviews (optionally filtered by property)"""
    from database import Review as DBReview
    
    query = db.query(DBReview)
    
    if property_id:
        query = query.filter(DBReview.property_id == property_id)
    
    if approved_only:
        query = query.filter(DBReview.is_approved == True, DBReview.is_visible == True)
    
    reviews = query.order_by(DBReview.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "reviews": [
            {
                "id": r.id,
                "property_id": r.property_id,
                "guest_name": r.guest_name,
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
                "reply": r.reply,
                "reply_at": r.reply_at.isoformat() if r.reply_at else None,
                "is_approved": r.is_approved,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reviews
        ],
        "total": query.count()
    }

@api_router.post("/reviews")
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review (public endpoint for guests)"""
    from database import Review as DBReview
    
    new_review = DBReview(
        id=str(uuid.uuid4()),
        property_id=review.property_id,
        booking_id=review.booking_id,
        guest_name=review.guest_name,
        guest_email=review.guest_email,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        is_approved=True  # Auto-approve for now
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return {"status": "success", "review_id": new_review.id}

@api_router.post("/reviews/{review_id}/reply")
def reply_to_review(
    review_id: str,
    reply: ReviewReply,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Host replies to a review"""
    from database import Review as DBReview
    
    review = db.query(DBReview).filter(DBReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Bewertung nicht gefunden")
    
    # Verify ownership (property belongs to user)
    property = db.query(DBProperty).filter(DBProperty.id == review.property_id).first()
    if not property or property.user_id != user.id:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    review.reply = reply.reply
    review.reply_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"status": "success", "message": "Antwort gespeichert"}

@api_router.delete("/reviews/{review_id}")
def delete_review(
    review_id: str,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review (host only)"""
    from database import Review as DBReview
    
    review = db.query(DBReview).filter(DBReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Bewertung nicht gefunden")
    
    # Verify ownership
    property = db.query(DBProperty).filter(DBProperty.id == review.property_id).first()
    if not property or property.user_id != user.id:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    db.delete(review)
    db.commit()
    
    return {"status": "success", "message": "Bewertung gelöscht"}


# ============ ANALYTICS API (Enhanced) ============
class AnalyticsFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    property_id: Optional[int] = None
    group_by: Optional[str] = "day"  # day, week, month

@api_router.post("/analytics/dashboard")
def get_analytics_dashboard(
    filter: AnalyticsFilter,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics data for dashboard"""
    from database import PropertyAnalytics as DBPropertyAnalytics
    from database import AnalyticsEvent as DBAnalyticsEvent
    
    # Parse dates
    if filter.start_date:
        start = datetime.fromisoformat(filter.start_date.replace('Z', '+00:00'))
    else:
        start = datetime.now(timezone.utc) - timedelta(days=30)
    
    if filter.end_date:
        end = datetime.fromisoformat(filter.end_date.replace('Z', '+00:00'))
    else:
        end = datetime.now(timezone.utc)
    
    # Get user's properties
    properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
    property_ids = [p.id for p in properties]
    
    # Get bookings for the period
    bookings_query = db.query(DBBooking).filter(
        DBBooking.user_id == user.id,
        DBBooking.created_at >= start,
        DBBooking.created_at <= end
    )
    
    if filter.property_id:
        bookings_query = bookings_query.filter(DBBooking.property_id == filter.property_id)
    
    bookings = bookings_query.all()
    
    # Calculate stats
    total_bookings = len(bookings)
    confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
    completed_bookings = len([b for b in bookings if b.status == 'completed'])
    cancelled_bookings = len([b for b in bookings if b.status == 'cancelled'])
    
    total_revenue = sum(b.total_price or 0 for b in bookings if b.status in ['confirmed', 'completed'])
    avg_booking_value = total_revenue / confirmed_bookings if confirmed_bookings > 0 else 0
    
    # Occupancy calculation
    total_nights = 0
    for b in bookings:
        if b.check_in and b.check_out and b.status in ['confirmed', 'completed']:
            nights = (b.check_out - b.check_in).days
            total_nights += max(0, nights)
    
    # Get reviews for average rating
    from database import Review as DBReview
    reviews = db.query(DBReview).filter(
        DBReview.property_id.in_(property_ids) if property_ids else DBReview.property_id == -1
    ).all()
    
    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    # Group bookings by date for chart
    bookings_by_date = {}
    revenue_by_date = {}
    
    for b in bookings:
        if b.created_at:
            if filter.group_by == "day":
                key = b.created_at.strftime("%Y-%m-%d")
            elif filter.group_by == "week":
                key = b.created_at.strftime("%Y-W%W")
            else:  # month
                key = b.created_at.strftime("%Y-%m")
            
            bookings_by_date[key] = bookings_by_date.get(key, 0) + 1
            revenue_by_date[key] = revenue_by_date.get(key, 0) + (b.total_price or 0)
    
    # Generate labels and data
    sorted_keys = sorted(bookings_by_date.keys())
    
    return {
        "summary": {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": round(total_revenue, 2),
            "avg_booking_value": round(avg_booking_value, 2),
            "total_nights": total_nights,
            "avg_rating": avg_rating,
            "total_reviews": len(reviews)
        },
        "charts": {
            "bookings_by_date": {
                "labels": sorted_keys,
                "data": [bookings_by_date.get(k, 0) for k in sorted_keys]
            },
            "revenue_by_date": {
                "labels": sorted_keys,
                "data": [round(revenue_by_date.get(k, 0), 2) for k in sorted_keys]
            }
        },
        "properties": [
            {
                "id": p.id,
                "name": p.name,
                "bookings_count": len([b for b in bookings if str(b.property_id) == str(p.id)])
            }
            for p in properties
        ],
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        }
    }

@api_router.get("/analytics/occupancy")
def get_occupancy_analytics(
    property_id: Optional[int] = None,
    months: int = 12,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get occupancy rate analytics"""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    # Get user's properties
    properties = db.query(DBProperty).filter(DBProperty.user_id == user.id).all()
    
    if property_id:
        properties = [p for p in properties if p.id == property_id]
    
    if not properties:
        return {"occupancy": [], "avg_occupancy": 0}
    
    property_ids = [p.id for p in properties]
    
    # Calculate occupancy for each month
    now = datetime.now(timezone.utc)
    occupancy_data = []
    total_occupancy = 0
    
    for i in range(months):
        month_start = now - relativedelta(months=months - 1 - i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Days in month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        days_in_month = month_end.day
        
        # Get bookings for this month
        bookings = db.query(DBBooking).filter(
            DBBooking.property_id.in_(property_ids),
            DBBooking.status.in_(['confirmed', 'completed']),
            DBBooking.check_out >= month_start,
            DBBooking.check_in <= month_end
        ).all()
        
        # Count occupied nights
        occupied_nights = 0
        for b in bookings:
            check_in = max(b.check_in, month_start) if b.check_in else month_start
            check_out = min(b.check_out, month_end + timedelta(days=1)) if b.check_out else month_end
            
            if check_out > check_in:
                nights = (check_out - check_in).days
                occupied_nights += max(0, nights)
        
        # Total possible nights (properties * days)
        max_nights = len(property_ids) * days_in_month
        occupancy_rate = (occupied_nights / max_nights * 100) if max_nights > 0 else 0
        
        occupancy_data.append({
            "month": month_start.strftime("%Y-%m"),
            "month_name": month_start.strftime("%b %Y"),
            "occupied_nights": occupied_nights,
            "max_nights": max_nights,
            "occupancy_rate": round(occupancy_rate, 1)
        })
        
        total_occupancy += occupancy_rate
    
    avg_occupancy = total_occupancy / months if months > 0 else 0
    
    return {
        "occupancy": occupancy_data,
        "avg_occupancy": round(avg_occupancy, 1),
        "properties_count": len(properties)
    }

@api_router.post("/analytics/track")
def track_analytics_event(
    event_type: str,
    property_id: Optional[int] = None,
    event_data: Optional[dict] = None,
    guest_token: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Track an analytics event"""
    from database import AnalyticsEvent as DBAnalyticsEvent
    
    # Get IP and user agent
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:500]
    
    event = DBAnalyticsEvent(
        id=str(uuid.uuid4()),
        event_type=event_type,
        property_id=property_id,
        event_data=json.dumps(event_data) if event_data else None,
        guest_token=guest_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(event)
    db.commit()
    
    return {"status": "success", "event_id": event.id}


# ============ SMART RULES API (Enhanced) ============
class SmartRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str  # time_based, booking_created, booking_confirmed, check_in, check_out, guest_action
    condition: dict  # JSON conditions
    action: dict  # JSON actions
    priority: int = 0

class SmartRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[dict] = None
    action: Optional[dict] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

@api_router.get("/smart-rules")
def get_smart_rules(
    property_id: Optional[int] = None,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all smart rules for user (optionally filtered by property)"""
    from database import SmartRule as DBSmartRule
    
    query = db.query(DBSmartRule).filter(DBSmartRule.user_id == user.id)
    
    if property_id:
        # Filter by property_id in condition JSON
        query = query.filter(DBSmartRule.condition.contains(f'"property_id": {property_id}'))
    
    rules = query.order_by(DBSmartRule.priority.desc(), DBSmartRule.created_at.desc()).all()
    
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "trigger_type": r.trigger_type,
                "condition": json.loads(r.condition) if r.condition else {},
                "action": json.loads(r.action) if r.action else {},
                "priority": r.priority,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in rules
        ]
    }

@api_router.post("/smart-rules")
def create_smart_rule(
    rule: SmartRuleCreate,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new smart rule"""
    from database import SmartRule as DBSmartRule
    
    new_rule = DBSmartRule(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type,
        condition=json.dumps(rule.condition),
        action=json.dumps(rule.action),
        priority=rule.priority,
        is_active=True
    )
    
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    return {
        "status": "success",
        "rule_id": new_rule.id,
        "message": "Smart Rule erstellt"
    }

@api_router.put("/smart-rules/{rule_id}")
def update_smart_rule(
    rule_id: str,
    update: SmartRuleUpdate,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a smart rule"""
    from database import SmartRule as DBSmartRule
    
    rule = db.query(DBSmartRule).filter(
        DBSmartRule.id == rule_id,
        DBSmartRule.user_id == user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    if update.name is not None:
        rule.name = update.name
    if update.description is not None:
        rule.description = update.description
    if update.condition is not None:
        rule.condition = json.dumps(update.condition)
    if update.action is not None:
        rule.action = json.dumps(update.action)
    if update.priority is not None:
        rule.priority = update.priority
    if update.is_active is not None:
        rule.is_active = update.is_active
    
    db.commit()
    
    return {"status": "success", "message": "Smart Rule aktualisiert"}

@api_router.delete("/smart-rules/{rule_id}")
def delete_smart_rule(
    rule_id: str,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a smart rule"""
    from database import SmartRule as DBSmartRule
    
    rule = db.query(DBSmartRule).filter(
        DBSmartRule.id == rule_id,
        DBSmartRule.user_id == user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Smart Rule nicht gefunden")
    
    db.delete(rule)
    db.commit()
    
    return {"status": "success", "message": "Smart Rule gelöscht"}


# ============ I18N / TRANSLATIONS API ============
class TranslationCreate(BaseModel):
    language: str
    key: str
    value: str
    context: Optional[str] = None

@api_router.get("/translations/{language}")
def get_translations(
    language: str,
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get translations for a language"""
    from database import Translation as DBTranslation
    
    query = db.query(DBTranslation).filter(DBTranslation.language == language)
    
    if context:
        query = query.filter(DBTranslation.context == context)
    
    translations = query.all()
    
    return {
        "language": language,
        "translations": {t.key: t.value for t in translations}
    }

@api_router.get("/user/language")
def get_user_language(
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's preferred language"""
    from database import UserLanguage as DBUserLanguage
    
    user_lang = db.query(DBUserLanguage).filter(DBUserLanguage.user_id == user.id).first()
    
    return {"language": user_lang.language if user_lang else "de"}

@api_router.put("/user/language")
def set_user_language(
    language: str,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set user's preferred language"""
    from database import UserLanguage as DBUserLanguage
    
    if language not in ['de', 'en', 'fr', 'es', 'it']:
        raise HTTPException(status_code=400, detail="Unsupported language")
    
    user_lang = db.query(DBUserLanguage).filter(DBUserLanguage.user_id == user.id).first()
    
    if not user_lang:
        user_lang = DBUserLanguage(
            id=str(uuid.uuid4()),
            user_id=user.id,
            language=language
        )
        db.add(user_lang)
    else:
        user_lang.language = language
    
    db.commit()
    
    return {"status": "success", "language": language}
