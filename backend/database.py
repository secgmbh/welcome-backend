from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os
import logging

# Logger für database module
logger = logging.getLogger(__name__)

Base = declarative_base()

# Wird in init_db() initialisiert
SessionLocal = None
engine = None

class User(Base):
    __tablename__ = "users"
    # Ignoriere die problematische is_ Spalte falls sie existiert
    __mapper_args__ = {
        'include_properties': [
            'id', 'email', 'password_hash', 'name', 'created_at',
            'is_demo', 'is_email_verified', 'email_verification_token', 
            'email_verification_token_expires', 'brand_color', 'logo_url',
            'invoice_name', 'invoice_address', 'invoice_zip', 'invoice_city',
            'invoice_country', 'invoice_vat_id', 'keysafe_location', 
            'keysafe_code', 'keysafe_instructions',
            # === NEU: User Management & Subscription ===
            'phone', 'company_name', 'plan', 'trial_ends_at', 
            'max_properties', 'stripe_customer_id', 'is_active'
        ]
    }
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(64), unique=True, index=True)
    email_verification_token_expires = Column(DateTime)
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
    # === NEU: User Management & Subscription ===
    phone = Column(String(50))  # Telefonnummer
    company_name = Column(String(200))  # Firmenname (optional)
    plan = Column(String(20), default='free')  # free, starter, pro, enterprise
    trial_ends_at = Column(DateTime)  # Trial-Ende (für paid plans)
    max_properties = Column(Integer, default=1)  # Max Properties je nach Plan
    stripe_customer_id = Column(String(100))  # Stripe Customer ID für Payments
    is_active = Column(Boolean, default=True)  # Account aktiv/deaktiviert

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Integer ID (kompatibel mit existierender DB)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    public_id = Column(String(20), nullable=True, index=True)  # Öffentliche ID für QR-Codes
    # Gästeseite Features
    image_url = Column(String(500), nullable=True)  # Hauptbild
    wifi_name = Column(String(100), nullable=True)  # WLAN Name
    wifi_password = Column(String(100), nullable=True)  # WLAN Passwort
    keysafe_location = Column(String(200), nullable=True)  # KeySafe Standort
    keysafe_code = Column(String(50), nullable=True)  # KeySafe Code/PIN
    keysafe_instructions = Column(Text, nullable=True)  # Anleitung
    checkin_time = Column(String(10), default="15:00")  # Check-in Zeit
    checkout_time = Column(String(10), default="11:00")  # Check-out Zeit
    host_phone = Column(String(50), nullable=True)  # Gastgeber Telefon
    host_email = Column(String(100), nullable=True)  # Gastgeber Email
    host_whatsapp = Column(String(50), nullable=True)  # WhatsApp Nummer
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
    commission_rate = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    user_id = Column(String(36), nullable=False, index=True)  # Owner (User)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PropertyCleaner(Base):
    """Zuweisung: Reinigungskraft <-> Property"""
    __tablename__ = "property_cleaners"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(Integer, nullable=False, index=True)
    cleaner_id = Column(String(36), nullable=False, index=True)
    notify_hours_before = Column(Integer, default=2)  # Stunden vor Checkout benachrichtigen
    is_primary = Column(Boolean, default=False)  # Haupt-Reinigungskraft
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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
    logger.info(f"[DB] Verbinde zu: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True, echo=False)
        logger.info(f"[DB] Engine erstellt")
        
        # Teste Connection
        with engine.connect() as conn:
            logger.info(f"[DB] ✓ Connection erfolgreich")
        
        # WICHTIG: Fehlende Spalten VOR create_all() hinzufügen (für bestehende Datenbanken)
        # Dies muss VOR create_all() passieren, damit neue Spalten verfügbar sind
        logger.info(f"[DB] Prüfe und füge fehlende Spalten hinzu...")
        try:
            with engine.connect() as conn:
                # Prüfe welche Tabellen existieren
                result = conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                existing_tables = [row[0] for row in result.fetchall()]
                logger.info(f"[DB] Existierende Tabellen: {existing_tables}")
                
                # Wenn users Tabelle existiert, füge fehlende Spalten hinzu
                if 'users' in existing_tables:
                    result = conn.execute(text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'users'
                    """))
                    existing_columns = [row[0] for row in result.fetchall()]
                    logger.info(f"[DB] Existierende users Spalten: {existing_columns}")
                    
                    # BEREINIGUNG: Lösche die problematische 'is_' Spalte falls vorhanden
                    # Diese Spalte wurde versehentlich erstellt und verursacht Fehler
                    if 'is_' in existing_columns:
                        try:
                            # DROP COLUMN benötigt explizites Commit in PostgreSQL
                            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS is_"))
                            logger.info(f"[DB] ✓ Executed DROP COLUMN is_")
                        except Exception as e:
                            logger.warning(f"[DB] ⚠️ Could not drop column is_: {e}")
                    # Commit außerhalb des try blocks um sicherzustellen dass es ausgeführt wird
                    try:
                        conn.commit()
                        logger.info(f"[DB] ✓ Schema changes committed")
                    except Exception as e:
                        logger.warning(f"[DB] ⚠️ Commit failed: {e}")
                    
                    # Fehlende Spalten hinzufügen
                    columns_to_add = [
                        ('is_demo', 'BOOLEAN DEFAULT FALSE'),
                        ('is_email_verified', 'BOOLEAN DEFAULT FALSE'),
                        ('email_verification_token', 'VARCHAR(64)'),
                        ('email_verification_token_expires', 'TIMESTAMP'),
                        ('brand_color', 'VARCHAR(7)'),
                        ('logo_url', 'VARCHAR(500)'),
                        ('invoice_name', 'VARCHAR(200)'),
                        ('invoice_address', 'VARCHAR(500)'),
                        ('invoice_zip', 'VARCHAR(20)'),
                        ('invoice_city', 'VARCHAR(100)'),
                        ('invoice_country', 'VARCHAR(100)'),
                        ('invoice_vat_id', 'VARCHAR(50)'),
                        ('keysafe_location', 'VARCHAR(500)'),
                        ('keysafe_code', 'VARCHAR(50)'),
                        ('keysafe_instructions', 'TEXT'),
                        # === NEU: User Management & Subscription ===
                        ('phone', 'VARCHAR(50)'),
                        ('company_name', 'VARCHAR(200)'),
                        ('plan', 'VARCHAR(20) DEFAULT \'free\''),
                        ('trial_ends_at', 'TIMESTAMP'),
                        ('max_properties', 'INTEGER DEFAULT 1'),
                        ('stripe_customer_id', 'VARCHAR(100)'),
                        ('is_active', 'BOOLEAN DEFAULT TRUE'),
                    ]
                    
                    added = []
                    for col_name, col_type in columns_to_add:
                        if col_name not in existing_columns:
                            try:
                                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                                conn.commit()
                                added.append(col_name)
                                logger.info(f"[DB] ✓ Added column to users: {col_name}")
                            except Exception as e:
                                logger.info(f"[DB] ✗ Failed to add {col_name}: {e}")
                                conn.rollback()
                    
                    if added:
                        logger.info(f"[DB] ✓ Added {len(added)} missing columns to users table")
                
                # Wenn properties Tabelle existiert, prüfe user_id Typ und füge fehlende Spalten hinzu
                if 'properties' in existing_tables:
                    result = conn.execute(text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'properties'
                    """))
                    existing_prop_columns = [row[0] for row in result.fetchall()]
                    
                    # Fehlende Spalten für properties
                    prop_columns_to_add = [
                        ('is_active', 'BOOLEAN DEFAULT TRUE'),
                        ('description', 'TEXT'),
                        ('address', 'VARCHAR(500)'),
                        ('keysafe_location', 'VARCHAR(500)'),
                        ('keysafe_code', 'VARCHAR(50)'),
                        ('keysafe_instructions', 'TEXT'),
                    ]
                    
                    for col_name, col_type in prop_columns_to_add:
                        if col_name not in existing_prop_columns:
                            try:
                                conn.execute(text(f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}"))
                                conn.commit()
                                logger.info(f"[DB] ✓ Added column to properties: {col_name}")
                            except Exception as e:
                                logger.info(f"[DB] ✗ Failed to add {col_name} to properties: {e}")
                                conn.rollback()
                    
                    # Prüfe user_id Typ
                    result = conn.execute(text("""
                        SELECT data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'properties' AND column_name = 'user_id'
                    """))
                    row = result.fetchone()
                    if row and 'int' in str(row[0]).lower():
                        logger.info(f"[DB] ⚠️  properties.user_id ist Integer - ändere zu VARCHAR(36)...")
                        conn.execute(text("ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR(36) USING user_id::VARCHAR(36)"))
                        conn.commit()
                        logger.info(f"[DB] ✓ user_id Spalte geändert zu VARCHAR(36)")
                        
        except Exception as e:
            logger.info(f"[DB] ⚠️  Konnte Migrationen nicht ausführen: {e}")
        
        # Erstelle fehlende Tabellen (für neue Installationen)
        logger.info(f"[DB] Erstelle fehlende Tables (falls nötig)...")
        Base.metadata.create_all(bind=engine)
        logger.info(f"[DB] ✓ Tables erstellt/geprüft")
        
        # Überprüfe ob Tables existieren
        insp = inspect(engine)
        tables = insp.get_table_names()
        logger.info(f"[DB] ✓ Existierende Tabellen: {tables}")
        
        # Erstelle Session Factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info(f"[DB] ✓ SessionLocal initialisiert")
        
        # Erstelle Demo-Benutzer wenn nicht vorhanden
        try:
            logger.info(f"[DB] Prüfe Demo-Benutzer...")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT id, email FROM users WHERE email = 'demo@welcome-link.de'"))
                existing = result.fetchone()
                
                if not existing:
                    import uuid
                    from datetime import datetime
                    demo_id = str(uuid.uuid4())
                    # Einfacher Password Hash für Demo (in Production sollte bcrypt verwendet werden)
                    import hashlib
                    password_hash = hashlib.sha256("Demo123!".encode()).hexdigest()
                    
                    conn.execute(text("""
                        INSERT INTO users (id, email, password_hash, name, created_at)
                        VALUES (:id, 'demo@welcome-link.de', :hash, 'Demo Benutzer', NOW())
                    """), {"id": demo_id, "hash": password_hash})
                    conn.commit()
                    logger.info(f"[DB] ✓ Demo-Benutzer erstellt")
        except Exception as e:
            logger.info(f"[DB] ⚠️  Konnte Demo-Benutzer nicht erstellen: {e}")
        
        return engine, SessionLocal
    except Exception as e:
        logger.info(f"[DB] ❌ ERROR: {str(e)}")
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


