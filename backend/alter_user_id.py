#!/usr/bin/env python3
"""
Fix user_id column type from INT to VARCHAR(36)
"""
import os
import sys

sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

from sqlalchemy import create_engine, text, inspect

def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL nicht gesetzt!")
        return
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Prüfe user_id Spalte Typ
        result = conn.execute(text("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND column_name = 'user_id'
        """))
        row = result.fetchone()
        
        if row:
            print(f"Current user_id type: {row[0]}")
            
            if 'int' in row[0].lower():
                print("user_id ist INT - muss VARCHAR(36) sein!")
                
                #ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR(36)
                conn.execute(text("ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR(36) USING user_id::VARCHAR(36)"))
                conn.commit()
                print("✓ user_id Spalte geändert zu VARCHAR(36)")
            else:
                print("user_id ist bereits VARCHAR - OK!")
        else:
            print("user_id Spalte nicht gefunden!")

if __name__ == "__main__":
    main()
