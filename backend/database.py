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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo = Column(Boolean, default=False)
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
        
        # Prüfe ob properties.user_id VARCHAR ist (für UUIDs)
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'properties' AND column_name = 'user_id'
                """)).fetchone()
                if result and 'int' in result[0].lower():
                    print(f"[DB] ⚠️  properties.user_id ist Integer, aber UUIDs werden gespeichert - ändere Spalte zu VARCHAR(36)...")
                    conn.execute(text("ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR(36) USING user_id::VARCHAR(36)"))
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
