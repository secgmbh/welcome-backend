#!/usr/bin/env python3
"""
Guestview Token Re-Initialization
Erstellt einen Guestview Token für den Demo User
"""
import os
import sys
import uuid
from datetime import datetime, timezone

# Importiere die needed modules
sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

# Verwende die alembic-basierte database.py
from database import get_database_url, init_db, User as DBUser, GuestView as DBGuestView

def main():
    print("=== Guestview Token Re-Initialization ===")
    
    # Erstelle DB (ohne DROP)
    database_url = get_database_url()
    print(f"DB URL: {database_url[:50]}...")
    
    from sqlalchemy import create_engine
    engine = create_engine(database_url, pool_pre_ping=True, echo=False)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        demo_email = "demo@welcome-link.de"
        demo_token = "demo-guest-view-token"
        
        # Hole Demo User
        user = db.query(DBUser).filter(DBUser.email == demo_email.lower()).first()
        
        if not user:
            print(f"✗ Demo-User nicht gefunden: {demo_email}")
            return
        
        print(f"✓ Demo-User gefunden: {user.email} (ID: {user.id})")
        
        # Prüfe ob Token existiert
        existing_token = db.query(DBGuestView).filter(DBGuestView.token == demo_token).first()
        
        if existing_token:
            print(f"✓ Guestview Token existiert bereits: {demo_token}")
            print(f"  -> Guestview URL: https://www.welcome-link.de/guestview/{demo_token}")
        else:
            # Erstelle Token
            guest_view = DBGuestView(
                id=str(uuid.uuid4()),
                user_id=user.id,
                token=demo_token,
                created_at=datetime.now(timezone.utc)
            )
            db.add(guest_view)
            db.commit()
            print(f"✓ Guestview Token erstellt: {demo_token}")
            print(f"  -> Guestview URL: https://www.welcome-link.de/guestview/{demo_token}")
        
        print("\n=== Fertig ===")
        
    except Exception as e:
        print(f"✗ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
