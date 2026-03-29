from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os

Base = declarative_base()

# Wird in init_db() initialisiert
SessionLocal = None
engine = None

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    phone = Column(String(50))
    company_name = Column(String(200))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)  # Admin-Rechte für Nutzerverwaltung
    email_verification_token = Column(String(64), index=True)  # Removed unique=True for SQLite NULL support
    email_verification_token_expires = Column(DateTime)
    # Subscription
    plan = Column(String(20), default='free')  # free, starter, pro, enterprise
    trial_ends_at = Column(DateTime)
    max_properties = Column(Integer, default=1)
    stripe_customer_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    # Branding
    brand_color = Column(String(7), default='#F27C2C')  # Hex Farbe
    logo_url = Column(String(500))
    # Invoice / Rechnungsdaten
    invoice_name = Column(String(200))
    invoice_address = Column(String(500))
    invoice_zip = Column(String(20))
    invoice_city = Column(String(100))
    invoice_country = Column(String(100))
    invoice_vat_id = Column(String(50))
    # Key-Safe Info
    keysafe_location = Column(String(500))
    keysafe_code = Column(String(50))
    keysafe_instructions = Column(Text)

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    # Property Image
    image_url = Column(String(500))
    # Key-Safe Info
    keysafe_location = Column(String(500))
    keysafe_code = Column(String(50))
    keysafe_instructions = Column(Text)
    # Check-in/Check-out
    checkin_time = Column(String(10), default="15:00")
    checkout_time = Column(String(10), default="11:00")
    # Branding
    brand_color = Column(String(7), default="#F27C2C")
    # Contact
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    # House Rules
    house_rules = Column(Text)  # JSON array stored as text
    # WiFi Info
    wifi_name = Column(String(100))
    wifi_password = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class StatusCheck(Base):
    __tablename__ = "status_checks"
    
    id = Column(String(36), primary_key=True)
    client_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GuestView(Base):
    __tablename__ = "guest_views"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    token = Column(String(36), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    variant_a_name = Column(String(100))
    variant_b_name = Column(String(100))
    variant_a_url = Column(String(500))
    variant_b_url = Column(String(500))
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Extra(Base):
    __tablename__ = "extras"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    stock = Column(Integer, default=0)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Bundle(Base):
    __tablename__ = "bundles"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BundleExtra(Base):
    __tablename__ = "bundle_extras"
    
    id = Column(String(36), primary_key=True)
    bundle_id = Column(String(36), nullable=False, index=True)
    extra_id = Column(String(36), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)  # Property owner
    property_id = Column(String(36), nullable=False, index=True)
    booking_id = Column(String(36), index=True)  # Optional: link to booking
    guest_name = Column(String(200))
    guest_email = Column(String(200))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    comment = Column(Text)
    pros = Column(Text)  # JSON array of positive points
    cons = Column(Text)  # JSON array of negative points
    would_recommend = Column(Boolean)  # Would recommend to others
    photos = Column(Text)  # JSON array of photo URLs
    is_public = Column(Boolean, default=False)  # Show on public profile
    is_verified = Column(Boolean, default=False)  # Verified stay
    response = Column(Text)  # Owner response
    response_at = Column(DateTime)  # When owner responded
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    guest_name = Column(String(200))
    guest_email = Column(String(200))
    guest_phone = Column(String(50))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    guests = Column(Integer)
    message = Column(Text)
    total_price = Column(Float)
    tipping_percentage = Column(Integer, default=0)
    tipping_amount = Column(Float, default=0)
    status = Column(String(50), default='pending')  # pending, confirmed, cancelled
    payment_method = Column(String(50))  # paypal, apple_pay, google_pay, none
    invoice_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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


class Cleaner(Base):
    """Reinigungskraft für Properties"""
    __tablename__ = "cleaners"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PropertyCleaner(Base):
    """Zuweisung Reinigungskraft zu Property"""
    __tablename__ = "property_cleaners"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    cleaner_id = Column(String(36), nullable=False, index=True)
    notify_hours_before = Column(Integer, default=24)  # Stunden vor Checkout
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# === NEW FEATURES (v2.9.0) ===

class CustomQuestion(Base):
    """Benutzerdefinierte Fragen für Gast-Intake"""
    __tablename__ = "custom_questions"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    question = Column(String(500), nullable=False)
    question_type = Column(String(20), default='text')  # text, multiple_choice, checkbox, number
    options = Column(Text)  # JSON für Multiple Choice Optionen
    required = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GuestAnswer(Base):
    """Antworten auf benutzerdefinierte Fragen"""
    __tablename__ = "guest_answers"
    
    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), nullable=False, index=True)
    booking_id = Column(String(36), nullable=False, index=True)
    guest_id = Column(String(36), index=True)
    answer = Column(Text)  # Text oder JSON für Multiple Choice
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RentalAgreement(Base):
    """Digitale Mietverträge"""
    __tablename__ = "rental_agreements"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    booking_id = Column(String(36), index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Agreement Content
    title = Column(String(200), nullable=False)
    content = Column(Text)  # Markdown/HTML template
    terms = Column(Text)  # JSON für strukturierte Terms
    
    # Custom Rules
    house_rules = Column(Text)  # JSON für Rules mit Penalties
    cancellation_policy = Column(Text)
    deposit_terms = Column(Text)
    
    # Signatures
    host_signature_url = Column(String(500))
    host_signed_at = Column(DateTime)
    guest_signature_url = Column(String(500))
    guest_signed_at = Column(DateTime)
    
    # Status
    status = Column(String(20), default='pending')  # pending, signed, cancelled
    
    # Legal
    ip_address_guest = Column(String(50))
    user_agent_guest = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SecurityDeposit(Base):
    """Kaution-Management"""
    __tablename__ = "security_deposits"
    
    id = Column(String(36), primary_key=True)
    booking_id = Column(String(36), nullable=False, index=True)
    property_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    status = Column(String(20), default='pending')  # pending, collected, returned, claimed
    
    # Payment
    payment_method = Column(String(50))  # stripe, paypal, etc.
    payment_id = Column(String(100))  # Stripe/PayPal ID
    payment_intent_id = Column(String(100))  # Stripe Payment Intent
    
    # Claims
    claim_amount = Column(Float)
    claim_reason = Column(Text)
    claim_status = Column(String(20))  # pending, approved, rejected
    claim_evidence = Column(Text)  # JSON für Photos, Documentation
    
    # Timestamps
    collected_at = Column(DateTime)
    returned_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class GuestVerification(Base):
    """Gast-Identitätsverifizierung"""
    __tablename__ = "guest_verifications"
    
    id = Column(String(36), primary_key=True)
    booking_id = Column(String(36), nullable=False, index=True)
    property_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    guest_name = Column(String(200), nullable=False)
    guest_email = Column(String(255), nullable=False)
    guest_phone = Column(String(50))
    
    # ID Document
    id_type = Column(String(50))  # passport, id_card, drivers_license
    id_document_url = Column(String(500))  # S3/Storage URL
    id_document_status = Column(String(20), default='pending')  # pending, verified, rejected
    
    # Selfie
    selfie_url = Column(String(500))
    selfie_status = Column(String(20), default='pending')
    
    # Verification Result
    verification_score = Column(Float)  # 0-100 confidence
    verification_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime)
    verified_by = Column(String(36))  # Admin user ID
    
    # GDPR
    retention_days = Column(Integer, default=90)  # Auto-delete after 90 days
    delete_at = Column(DateTime)


class AgreementTemplate(Base):
    """Vorlagen für Mietverträge"""
    __tablename__ = "agreement_templates"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Markdown/HTML template
    variables = Column(Text)  # JSON für Template-Variablen
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ApiKey(Base):
    """API Keys für externe Integrationen"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)  # wl_xxx format
    name = Column(String(100))  # Friendly name
    permissions = Column(Text)  # JSON: ['read', 'write', 'admin']
    rate_limit = Column(Integer, default=100)  # Requests per minute
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)  # Optional expiration
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    """Audit Logging für Sicherheitsereignisse"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    action = Column(String(50), nullable=False)  # login, logout, api_call, data_access, etc.
    resource = Column(String(100))  # property, booking, user, etc.
    resource_id = Column(String(36))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    details = Column(Text)  # JSON für zusätzliche Details
    status = Column(String(20), default='success')  # success, failed, blocked
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


def get_database_url():
    """Erstelle Database URL aus Umgebungsvariablen"""
    # Bevorzuge DATABASE_URL (PostgreSQL Connection String von Render)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Fallback: Baue URL aus einzelnen Komponenten
    db_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')
    db_port = os.environ.get('DB_PORT', '5432')
    
    if not all([db_host, db_user, db_password, db_name]):
        # Fallback zu SQLite für lokale Entwicklung
        return "sqlite:///./app.db"
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def init_db():
    """Initialisiere Datenbank und erstelle Tabellen"""
    global SessionLocal, engine
    
    database_url = get_database_url()
    print(f"[DB] Verbinde zu: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True, echo=False)
        print(f"[DB] Engine erstellt")
        
        # Teste Connection
        with engine.connect() as conn:
            print(f"[DB] ✓ Connection erfolgreich")
        
        # Erstelle fehlende Tabellen (Fallback für neue Installationen)
        # Schema-Änderungen werden über Alembic Migrations verwaltet
        print(f"[DB] Erstelle fehlende Tables (falls nötig)...")
        Base.metadata.create_all(bind=engine)
        print(f"[DB] ✓ Tables erstellt/geprüft")
        
        # Überprüfe ob Tables existieren
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"[DB] ✓ Existierende Tabellen: {tables}")
        
        # === FEHLENDE SPALTEN HINZUFÜGEN (Safe Migration) ===
        # Diese Spalten fehlen in Production und werden automatisch hinzugefügt
        # Nutzt SQLAlchemy inspect() für DB-unabhängige Column-Erkennung
        missing_columns = [
            # User Management & Subscription (v2.9.0+)
            ("users", "phone", "VARCHAR(50)"),
            ("users", "company_name", "VARCHAR(200)"),
            ("users", "plan", "VARCHAR(20) DEFAULT 'free'"),
            ("users", "trial_ends_at", "TIMESTAMP"),
            ("users", "max_properties", "INTEGER DEFAULT 1"),
            ("users", "stripe_customer_id", "VARCHAR(100)"),
            ("users", "is_active", "BOOLEAN DEFAULT TRUE"),
            ("users", "is_admin", "BOOLEAN DEFAULT FALSE"),
            # Invoice Felder
            ("users", "invoice_name", "VARCHAR(200)"),
            ("users", "invoice_address", "VARCHAR(500)"),
            ("users", "invoice_zip", "VARCHAR(20)"),
            ("users", "invoice_city", "VARCHAR(100)"),
            ("users", "invoice_country", "VARCHAR(100)"),
            ("users", "invoice_vat_id", "VARCHAR(50)"),
            # Branding Felder
            ("users", "brand_color", "VARCHAR(20)"),
            ("users", "logo_url", "VARCHAR(500)"),
            # Keysafe Felder
            ("users", "keysafe_location", "VARCHAR(500)"),
            ("users", "keysafe_code", "VARCHAR(100)"),
            ("users", "keysafe_instructions", "TEXT"),
            # Email verification
            ("users", "is_email_verified", "BOOLEAN DEFAULT FALSE"),
            ("users", "email_verification_token", "VARCHAR(64)"),
            ("users", "email_verification_token_expires", "TIMESTAMP"),
        ]
        
        for table_name, column, col_type in missing_columns:
            try:
                # DB-unabhängige Column-Erkennung mit SQLAlchemy inspect()
                existing_columns = [col['name'] for col in insp.get_columns(table_name)]
                if column not in existing_columns:
                    print(f"[DB] + Füge {table_name}.{column} hinzu...")
                    with engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column} {col_type}"))
                        conn.commit()
                    print(f"[DB] ✓ {table_name}.{column} hinzugefügt")
            except Exception as e:
                print(f"[DB] ⚠️  Konnte {table_name}.{column} nicht prüfen/hinzufügen: {e}")
        
        # Entferne UNIQUE Constraint von email_verification_token (SQLite kann keine NULL-Werte)
        # Erstelle normalen Index für schnellere Suche
        try:
            with engine.connect() as conn:
                # Drop old UNIQUE index if exists
                conn.execute(text("DROP INDEX IF EXISTS ix_users_email_verification_token"))
                conn.commit()
                print(f"[DB] ✓ Alter Index entfernt")
                # Create new non-unique index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_email_verification_token 
                    ON users (email_verification_token)
                """))
                conn.commit()
                print(f"[DB] ✓ Neuer Index erstellt (non-unique)")
        except Exception as e:
            print(f"[DB] ⚠️  Index konnte nicht erstellt werden: {e}")
        
        # Prüfe ob properties.user_id VARCHAR ist (für UUIDs) - DB-unabhängig
        try:
            props_columns = {col['name']: col['type'] for col in insp.get_columns('properties')}
            if 'user_id' in props_columns:
                col_type = str(props_columns['user_id']).upper()
                if 'INT' in col_type and 'VARCHAR' not in col_type:
                    print(f"[DB] ⚠️  properties.user_id ist Integer, ändere zu VARCHAR(36)...")
                    # SQLite/PostgreSQL kompatibel
                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR(36)"))
                        conn.commit()
                    print(f"[DB] ✓ user_id Spalte geändert zu VARCHAR(36)")
        except Exception as e:
            print(f"[DB] ⚠️  Konnte user_id Spalte nicht prüfen/ändern: {e}")
        
        # Erstelle Session Factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print(f"[DB] ✓ SessionLocal initialisiert")
        
        return engine, SessionLocal
    except Exception as e:
        print(f"[DB] ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def get_db():
    """Dependency für FastAPI - gibt DB Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
