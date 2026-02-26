from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, inspect
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
