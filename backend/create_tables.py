#!/usr/bin/env python3
"""
DB Table Creation Script
Erstellt fehlende Tabellen für die Welcome Link API
"""
import os
import sys

# Importiere die needed modules
sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

from database import get_database_url, init_db, User as DBUser, Property as DBProperty, GuestView as DBGuestView, StatusCheck as DBStatusCheck

def main():
    print("=== DB Table Creation ===")
    
    # Erstelle DB
    database_url = get_database_url()
    print(f"DB URL: {database_url[:50]}...")
    
    from sqlalchemy import create_engine
    engine = create_engine(database_url, pool_pre_ping=True, echo=True)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Erstelle alle Tabellen
        from database import Base
        Base.metadata.create_all(bind=engine)
        
        # Check tabellen
        from sqlalchemy import inspect
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"✓ Existierende Tabellen: {tables}")
        
        # Prüfe ob guest_views existiert
        if 'guest_views' in tables:
            print("✓ guest_views Tabelle existiert")
        else:
            print("✗ guest_views Tabelle existiert NICHT")
        
        # Prüfe ob properties existiert
        if 'properties' in tables:
            print("✓ properties Tabelle existiert")
        else:
            print("✗ properties Tabelle existiert NICHT")
        
        # Prüfe ob users existiert
        if 'users' in tables:
            print("✓ users Tabelle existiert")
        else:
            print("✗ users Tabelle existiert NICHT")
        
        print("\n=== Fertig ===")
        
    except Exception as e:
        print(f"✗ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
