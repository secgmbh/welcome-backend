from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text
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
    engine = create_engine(database_url, pool_pre_ping=True, echo=False)
    
    # Erstelle alle Tabellen
    Base.metadata.create_all(bind=engine)
    
    # Erstelle Session Factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

def get_db():
    """Dependency für FastAPI - gibt DB Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
