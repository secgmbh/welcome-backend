#!/usr/bin/env python3
"""
Demo User Re-Initialization Script - Quick Version
Erstellt Demo-User mit Guestview Token und Properties
ohne Passworthash (fuer SQLite Demo)
"""
import os
import sys
import uuid
from datetime import datetime, timezone
import sqlite3

# Importiere die needed modules
sys.path.insert(0, '/data/.openclaw/workspace/welcome-backend/backend')

# Verwende die alembic-basierte database.py
from database import get_database_url, init_db, User as DBUser, Property as DBProperty, GuestView as DBGuestView

def main():
    print("=== Demo User Quick Re-Initialization ===")
    
    # Erstelle DB
    database_url = get_database_url()
    print(f"DB URL: {database_url[:50]}...")
    
    # Verbinde direkt zu SQLite
    if 'sqlite' in database_url:
        db_path = database_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Erstelle Demo User mit einem einfachen Hash
        demo_email = "demo@welcome-link.de"
        demo_password_hash = "pbkdf2:sha256:600000$test$abc"  # Beispiel hash
        
        # Prüfe ob User existiert
        cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email.lower(),))
        existing = cursor.fetchone()
        
        if existing:
            user_id = existing[0]
            print(f"✓ Demo-User existiert bereits: {demo_email}")
        else:
            # Erstelle User
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, name, created_at, is_demo, invoice_name, invoice_address, invoice_zip, invoice_city, invoice_country, invoice_vat_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                demo_email.lower(),
                demo_password_hash,
                "Demo Benutzer",
                datetime.now(timezone.utc).isoformat(),
                1,
                "Alpenblick Hospitality GmbH",
                "Bergstraße 12",
                "82467",
                "Garmisch-Partenkirchen",
                "Deutschland",
                "DE123456789"
            ))
            print(f"✓ Demo-User erstellt: {demo_email}")
        
        # Prüfe Properties
        cursor.execute("SELECT COUNT(*) FROM properties WHERE user_id = ?", (user_id,))
        prop_count = cursor.fetchone()[0]
        
        if prop_count == 0:
            # Erstelle Demo Properties
            demo_properties = [
                ("Boutique Hotel Alpenblick", "Charmantes 4-Sterne Hotel mit Bergpanorama in Garmisch-Partenkirchen. 45 Zimmer, Spa-Bereich und regionale Küche.", "Zugspitzstraße 42, 82467 Garmisch-Partenkirchen"),
                ("Ferienwohnung Seeblick", "Moderne 3-Zimmer Ferienwohnung direkt am Bodensee mit eigenem Bootssteg und Panoramaterrasse.", "Seepromenade 15, 88131 Lindau"),
                ("Stadtapartment München City", "Stilvolles Apartment im Herzen Münchens, perfekt für Geschäftsreisende. 5 Min. zum Marienplatz.", "Maximilianstraße 28, 80539 München")
            ]
            
            for name, desc, addr in demo_properties:
                prop_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO properties (id, user_id, name, description, address, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (prop_id, user_id, name, desc, addr, datetime.now(timezone.utc).isoformat()))
            print(f"✓ 3 Properties erstellt")
        else:
            print(f"✓ {prop_count} Properties existieren bereits")
        
        # Prüfe Guestview Token
        demo_guestview_token = "demo-guest-view-token"
        cursor.execute("SELECT id FROM guest_views WHERE token = ?", (demo_guestview_token,))
        existing_token = cursor.fetchone()
        
        if existing_token:
            print(f"✓ Guestview Token existiert bereits: {demo_guestview_token}")
        else:
            # Erstelle Guestview Token
            guestview_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO guest_views (id, user_id, token, created_at)
                VALUES (?, ?, ?, ?)
            """, (guestview_id, user_id, demo_guestview_token, datetime.now(timezone.utc).isoformat()))
            print(f"✓ Guestview Token erstellt: {demo_guestview_token}")
        
        conn.commit()
        conn.close()
        
        print("\n=== Fertig ===")
        print(f"Demo-Login: {demo_email} / Demo123!")
        print(f"Guestview: https://www.welcome-link.de/guestview/{demo_guestview_token}")
    else:
        print("Nur SQLite support für dieses Script")

if __name__ == "__main__":
    main()
