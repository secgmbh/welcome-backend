#!/usr/bin/env python3
"""
Demo User Re-Initialization Script
Erstellt Demo-User mit Guestview Token und Properties
"""
import os
import sys
import uuid
from datetime import datetime, timezone

# Importiere die needed modules
sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

from database import get_database_url, init_db, User as DBUser, Property as DBProperty, GuestView as DBGuestView
from passlib.context import CryptContext

# Passwort Hash Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def main():
    print("=== Demo User Re-Initialization ===")
    
    # Erstelle DB
    engine, SessionLocal = init_db()
    db = SessionLocal()
    
    try:
        # Demo Credentials
        demo_email = "demo@welcome-link.de"
        demo_password = "Demo123!"
        
        # Prüfe ob User existiert
        existing = db.query(DBUser).filter(DBUser.email == demo_email.lower()).first()
        
        if existing:
            print(f"✓ Demo-User existiert bereits: {existing.email}")
        else:
            print(f"Erstelle Demo-User: {demo_email}")
            demo_user = DBUser(
                id=str(uuid.uuid4()),
                email=demo_email.lower(),
                password_hash=hash_password(demo_password),
                name="Demo Benutzer",
                created_at=datetime.now(timezone.utc),
                is_demo=True,
                invoice_name="Alpenblick Hospitality GmbH",
                invoice_address="Bergstraße 12",
                invoice_zip="82467",
                invoice_city="Garmisch-Partenkirchen",
                invoice_country="Deutschland",
                invoice_vat_id="DE123456789"
            )
            db.add(demo_user)
            db.commit()
            print(f"✓ Demo-User erstellt: {demo_email}")
            
            # Erstelle Demo Properties
            demo_properties = [
                DBProperty(
                    id=str(uuid.uuid4()),
                    user_id=demo_user.id,
                    name="Boutique Hotel Alpenblick",
                    description="Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.",
                    address="Zugspitzstraße 42, 82467 Garmisch-Partenkirchen",
                    created_at=datetime.now(timezone.utc)
                ),
                DBProperty(
                    id=str(uuid.uuid4()),
                    user_id=demo_user.id,
                    name="Ferienwohnung Seeblick",
                    description="Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.",
                    address="Seepromenade 15, 88131 Lindau",
                    created_at=datetime.now(timezone.utc)
                ),
                DBProperty(
                    id=str(uuid.uuid4()),
                    user_id=demo_user.id,
                    name="Stadtapartment München City",
                    description="Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.",
                    address="Maximilianstraße 28, 80539 München",
                    created_at=datetime.now(timezone.utc)
                )
            ]
            
            for prop in demo_properties:
                db.add(prop)
            db.commit()
            print(f"✓ 3 Properties erstellt")
            
            # Erstelle Guestview Token
            demo_guestview_token = "demo-guest-view-token"
            guest_view = DBGuestView(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                token=demo_guestview_token,
                created_at=datetime.now(timezone.utc)
            )
            db.add(guest_view)
            db.commit()
            print(f"✓ Guestview Token erstellt: {demo_guestview_token}")
            print(f"  -> Guestview URL: https://www.welcome-link.de/guestview/{demo_guestview_token}")
        
        print("\n=== Fertig ===")
        print(f"Demo-Login: {demo_email} / {demo_password}")
        print(f"Guestview: https://www.welcome-link.de/guestview/{demo_guestview_token}")
        
    except Exception as e:
        print(f"✗ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
