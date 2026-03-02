#!/usr/bin/env python3
"""
Fix Script: Entferne die problematische 'is_' Spalte aus der users Tabelle
Wird beim Server Start ausgeführt falls die Spalte existiert
"""
import os
import sys
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_is_column():
    """Entferne die is_ Spalte falls sie existiert"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.info("[FIX] Keine DATABASE_URL - SQLite Mode, überspringe")
        return True
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Prüfe ob users Tabelle existiert
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'users'
            """))
            
            if not result.fetchone():
                logger.info("[FIX] users Tabelle existiert nicht - überspringe")
                return True
            
            # Prüfe ob is_ Spalte existiert
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'is_'
            """))
            
            if result.fetchone():
                logger.info("[FIX] Lösche problematische is_ Spalte...")
                conn.execute(text("ALTER TABLE users DROP COLUMN is_"))
                conn.commit()
                logger.info("[FIX] ✓ is_ Spalte erfolgreich gelöscht")
            else:
                logger.info("[FIX] is_ Spalte nicht vorhanden - OK")
                
        return True
                
    except Exception as e:
        logger.error(f"[FIX] Fehler beim Fix: {e}")
        # Nicht werfen - der Server soll trotzdem starten
        return False

if __name__ == "__main__":
    # Load .env if exists
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        load_dotenv(Path(__file__).parent / '.env')
    except:
        pass
    
    success = fix_is_column()
    sys.exit(0 if success else 1)