from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

Base = declarative_base()

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
    db_host = os.environ.get('DB_HOST', 'jts0.your-database.de')
    db_user = os.environ.get('DB_USER', 'npuqdy_1')
    db_password = os.environ.get('DB_PASSWORD', 'c4]GK&$&-Xn4')
    db_name = os.environ.get('DB_NAME', 'npuqdy_db1')
    
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"

def init_db():
    """Initialisiere Datenbank und erstelle Tabellen"""
    database_url = get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True, echo=False)
    
    # Erstelle alle Tabellen
    Base.metadata.create_all(bind=engine)
    
    # Erstelle Session Factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

def get_db():
    """Dependency für FastAPI - gibt DB Session"""
    from server import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
