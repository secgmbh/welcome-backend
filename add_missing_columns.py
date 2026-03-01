#!/usr/bin/env python3
"""
Add missing columns to users table for demo registration fix.
This adds the missing columns without dropping any data.
"""
import os
import sys
from pathlib import Path

# Setup environment
ROOT_DIR = Path(__file__).parent
os.chdir(ROOT_DIR)
os.environ.setdefault('ENVIRONMENT', 'production')

from sqlalchemy import create_engine, text
from database import get_database_url

def add_missing_columns():
    """Füge fehlende Spalten zur users table hinzu"""
    print("=" * 60)
    print("ADD MISSING COLUMNS START")
    print("=" * 60)
    
    database_url = get_database_url()
    print(f"[1/3] DATABASE_URL: {database_url[:50]}...")
    
    try:
        # Erstelle Engine
        print("[2/3] Erstelle Engine...")
        engine = create_engine(database_url, pool_pre_ping=True)
        print("      ✓ Engine erstellt")
        
        with engine.begin() as conn:
            # Prüfe existierende Spalten
            print("[3/3] Prüfe und füge fehlende Spalten hinzu...")
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
                else:
                    print(f"      ℹ️  Column {col_name} already exists")
            
            if added:
                print(f"\n✓ Added {len(added)} missing columns: {added}")
            else:
                print("\n✓ All columns are present!")
        
        print("=" * 60)
        print("ADD MISSING COLUMNS SUCCESSFUL")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = add_missing_columns()
    sys.exit(0 if success else 1)
