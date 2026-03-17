#!/usr/bin/env python3
"""
Reset database script - löscht alle Tabellen und erstellt sie neu.
Nützlich für Render nach Fehlern oder Schema-Änderungen.
"""
import os
import sys
from pathlib import Path

# Setup environment
ROOT_DIR = Path(__file__).parent
os.chdir(ROOT_DIR)
os.environ.setdefault('ENVIRONMENT', 'production')

# Import after env setup
from sqlalchemy import create_engine, inspect
from database import Base, get_database_url

def reset_database():
    """Datenbank zurücksetzen - alle Tabellen löschen und neu erstellen"""
    print("=" * 60)
    print("DATABASE RESET START")
    print("=" * 60)
    
    database_url = get_database_url()
    print(f"[1/4] DATABASE_URL: {database_url[:50]}...")
    
    try:
        # Erstelle Engine
        print("[2/4] Erstelle Engine...")
        engine = create_engine(database_url, pool_pre_ping=True)
        print("      ✓ Engine erstellt")
        
        # Prüfe existierende Tabellen
        print("[3/4] Prüfe existierende Tabellen...")
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"      Aktuelle Tabellen: {tables}")
        
        if tables:
            print("[3a/4] Lösche alle Tabellen mit CASCADE...")
            # Drop alle Tabellen einzeln (reihenfolge wichtig wegen foreign keys)
            with engine.begin() as conn:
                # Drop in umgekehrter Reihenfolge (abhaengigkeiten auflösen)
                for table_name in reversed(tables):
                    print(f"      Drop table: {table_name}")
                    conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            print("      ✓ Alle Tabellen gelöscht")
        else:
            print("      ℹ️  Keine Tabellen zum Löschen")
        
        # Erstelle alle Tabellen neu
        print("[4/4] Erstelle Tabellen neu...")
        Base.metadata.create_all(bind=engine)
        print("      ✓ Tabellen erstellt")
        
        # Verifiziere
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"\n✓ Erstellte Tabellen: {tables}")
        
        # Falls columns fehlen (nach Schema-Updates), füge sie hinzu
        if 'users' in tables:
            print("[4b/4] Prüfe fehlende Spalten in users table...")
            with engine.begin() as conn:
                # Prüfe existierende Spalten
                result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users'
                """))
                existing = [row[0] for row in result.fetchall()]
                
                # Fehlende Spalten hinzufügen
                columns_to_add = [
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
                ]
                
                added = []
                for col_name, col_type in columns_to_add:
                    if col_name not in existing:
                        try:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                            added.append(col_name)
                            print(f"      ✓ Added column: {col_name}")
                        except Exception as e:
                            print(f"      ✗ Failed to add {col_name}: {e}")
                
                if added:
                    print(f"      ✓ Added {len(added)} missing columns")
                else:
                    print("      ℹ️  All columns present")
        
        print("=" * 60)
        print("DATABASE RESET SUCCESSFUL")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
