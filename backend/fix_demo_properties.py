#!/usr/bin/env python3
"""
Fix Demo Properties - inserit directly into DB
"""
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL nicht gesetzt!")
        return
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        demo_email = "demo@welcome-link.de"
        
        # Hole User ID
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": demo_email.lower()})
        user_row = result.fetchone()
        
        if not user_row:
            print(f"Demo User nicht gefunden: {demo_email}")
            return
        
        user_id = str(user_row[0])
        print(f"Demo User ID: {user_id}")
        
        # Insert Properties mit raw SQL (um UUID問題 zu vermeiden)
        properties = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Boutique Hotel Alpenblick",
                "description": "Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.",
                "address": "Zugspitzstraße 42, 82467 Garmisch-Partenkirchen",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Ferienwohnung Seeblick",
                "description": "Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.",
                "address": "Seepromenade 15, 88131 Lindau",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Stadtapartment München City",
                "description": "Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.",
                "address": "Maximilianstraße 28, 80539 München",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for prop in properties:
            stmt = text("""
                INSERT INTO properties (id, user_id, name, description, address, created_at)
                VALUES (:id, :user_id, :name, :description, :address, :created_at)
            """)
            db.execute(stmt, prop)
        
        db.commit()
        print(f"✓ 3 Properties eingefügt")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
