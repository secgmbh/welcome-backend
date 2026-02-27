#!/usr/bin/env python3
"""
Recreate demo user and properties
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
        # Lösche alle Tabellen neu - aber das wird fehlschlagen!
        # Stattdessen nur properties löschen und neu erstellen
        print("Recreating demo data...")
        
        # Lösche properties
        db.execute(text("DELETE FROM properties"))
        db.commit()
        print("✓ Properties gelöscht")
        
        # Hole demo user
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": "demo@welcome-link.de"})
        row = result.fetchone()
        
        if not row:
            print("Demo user nicht gefunden!")
            return
        
        user_id = str(row[0])
        print(f"User ID: {user_id}")
        
        # Insert properties
        properties = [
            (str(uuid.uuid4()), user_id, "Boutique Hotel Alpenblick", "Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.", "Zugspitzstraße 42, 82467 Garmisch-Partenkirchen"),
            (str(uuid.uuid4()), user_id, "Ferienwohnung Seeblick", "Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.", "Seepromenade 15, 88131 Lindau"),
            (str(uuid.uuid4()), user_id, "Stadtapartment München City", "Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.", "Maximilianstraße 28, 80539 München"),
        ]
        
        for p in properties:
            db.execute(text("""
                INSERT INTO properties (id, user_id, name, description, address, created_at)
                VALUES (:id, :user_id, :name, :description, :address, :created_at)
            """), {
                "id": p[0],
                "user_id": p[1],
                "name": p[2],
                "description": p[3],
                "address": p[4],
                "created_at": datetime.now(timezone.utc)
            })
        
        db.commit()
        print("✓ Properties neu eingefügt")
        
        # Reinitialize guestview token
        db.execute(text("DELETE FROM guest_views WHERE token = :token"), {"token": "demo-guest-view-token"})
        db.commit()
        print("✓ Guestview Token gelöscht")
        
        db.execute(text("""
            INSERT INTO guest_views (id, user_id, token, created_at)
            VALUES (:id, :user_id, :token, :created_at)
        """), {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "token": "demo-guest-view-token",
            "created_at": datetime.now(timezone.utc)
        })
        db.commit()
        print("✓ Guestview Token neu erstellt")
        
        print("Fertig!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
