#!/usr/bin/env python3
"""
Reset database script - löscht alle Tabellen und erstellt sie neu.
Nützlich für Render nach Fehlern oder Schema-Änderungen.
"""
import os
from pathlib import Path

# Setup environment
ROOT_DIR = Path(__file__).parent
os.chdir(ROOT_DIR)
os.environ.setdefault('ENVIRONMENT', 'production')

from database import init_db, Base, engine

def reset_database():
    """Datenbank zurücksetzen - alle Tabellen löschen und neu erstellen"""
    print("=" * 60)
    print("DATABASE RESET START")
    print("=" * 60)
    
    try:
        print("[1/4] Prüfe Datenbankverbindung...")
        database_url = os.environ.get('DATABASE_URL', 'nicht gesetzt')
        print(f"      DATABASE_URL: {database_url[:20]}...")
        
        print("[2/4] Öffne Verbindung...")
        engine, SessionLocal = init_db()
        print("      ✓ Verbindung hergestellt")
        
        print("[3/4] Lösche alle Tabellen...")
        Base.metadata.drop_all(bind=engine)
        print("      ✓ Tabellen gelöscht")
        
        print("[4/4] Erstelle Tabellen neu...")
        Base.metadata.create_all(bind=engine)
        print("      ✓ Tabellen erstellt")
        
        print("=" * 60)
        print("DATABASE RESET SUCCESSFUL")
        print("=" * 60)
        
        # Zeige erstellte Tabellen
        from sqlalchemy import inspect
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"\nErstellte Tabellen: {tables}")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = reset_database()
    exit(0 if success else 1)
