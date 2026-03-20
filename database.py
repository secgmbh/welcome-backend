from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, Float, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(64), unique=True, index=True)
    email_verification_token_expires = Column(DateTime)
    # User Management & Subscription (v2.9.0+)
    phone = Column(String(50))
    company_name = Column(String(200))
    plan = Column(String(20), default='free')
    trial_ends_at = Column(DateTime)
    max_properties = Column(Integer, default=1)
    stripe_customer_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    # Invoice details for hosting
    invoice_name = Column(String(200))
    invoice_address = Column(String(500))
    invoice_zip = Column(String(20))
    invoice_city = Column(String(100))
    invoice_country = Column(String(100))
    invoice_vat_id = Column(String(50))
    # Branding
    brand_color = Column(String(20))
    logo_url = Column(String(500))
    # Key safe
    keysafe_location = Column(String(500))
    keysafe_code = Column(String(100))
    keysafe_instructions = Column(Text)

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(String(500))
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
    title = Column(String(200))
    content = Column(Text)
    image_url = Column(String(500))
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Extra(Base):
    __tablename__ = "extras"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200))
    description = Column(Text)
    price = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Bundle(Base):
    __tablename__ = "bundles"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200))
    description = Column(Text)
    price = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BundleExtra(Base):
    __tablename__ = "bundle_extras"
    
    id = Column(String(36), primary_key=True)
    bundle_id = Column(String(36), nullable=False, index=True)
    extra_id = Column(String(36), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200))
    variant_a_name = Column(String(100))
    variant_b_name = Column(String(100))
    variant_a_url = Column(String(500))
    variant_b_url = Column(String(500))
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Partner(Base):
    __tablename__ = "partners"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200))
    description = Column(Text)
    category = Column(String(100))
    address = Column(String(500))
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(500))
    image_url = Column(String(500))
    commission_rate = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SmartRule(Base):
    __tablename__ = "smart_rules"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200))
    description = Column(Text)
    trigger_type = Column(String(100))
    condition = Column(Text)
    action = Column(Text)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    guest_name = Column(String(200))
    guest_email = Column(String(255))
    guest_phone = Column(String(50))
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    guests = Column(Integer, default=1)
    message = Column(Text)
    total_price = Column(Float, default=0)
    tipping_percentage = Column(Integer, default=0)
    tipping_amount = Column(Float, default=0)
    status = Column(String(50), default='pending')
    payment_method = Column(String(100))
    invoice_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    property_id = Column(String(36), nullable=False, index=True)
    cleaner_id = Column(String(36))
    title = Column(String(200))
    description = Column(Text)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
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
    """Initialisiere Datenbank - PRODUKTIONSSICHER (kein Datenverlust)"""
    global SessionLocal, engine
    
    database_url = get_database_url()
    print(f"[DB] Verbinde zu: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True, echo=False)
        print(f"[DB] Engine erstellt")
        
        # Teste Connection
        with engine.connect() as conn:
            print(f"[DB] ✓ Connection erfolgreich")
        
        # NICHT Tabellen löschen in Production!
        # Base.metadata.create_all() ist sicher - fügt nur fehlende Tabellen hinzu
        print(f"[DB] Erstelle/aktualisiere Tables...")
        Base.metadata.create_all(bind=engine)
        print(f"[DB] ✓ Tables erstellt")
        
        # Füge fehlende Spalten zu existierenden Tabellen hinzu (sicher)
        # WICHTIG: ALTER TABLE ... ADD COLUMN IF NOT EXISTS
        missing_columns = [
            # User Management & Subscription Felder (v2.9.0+)
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
        
        for table, column, col_type in missing_columns:
            try:
                with engine.connect() as conn:
                    result = conn.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = '{column}'
                    """).fetchone()
                    if not result:
                        print(f"[DB] + Füge {table}.{column} hinzu...")
                        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                        conn.commit()
                        print(f"[DB] ✓ {table}.{column} hinzugefügt")
            except Exception as e:
                print(f"[DB] ⚠️  Konnte {table}.{column} nicht prüfen/hinzufügen: {e}")
        
        # Erstelle Index für email_verification_token falls nicht vorhanden
        try:
            with engine.connect() as conn:
                conn.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_verification_token 
                    ON users (email_verification_token)
                """)
                conn.commit()
                print(f"[DB] ✓ Index erstellt")
        except Exception as e:
            print(f"[DB] ⚠️  Index konnte nicht erstellt werden: {e}")
        
        # Überprüfe ob Tables existieren
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"[DB] ✓ Tabellen: {tables}")
        
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
