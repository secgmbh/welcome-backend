#!/usr/bin/env python3
"""
Generate downloadable PDF resources for Welcome-Link
Simplified version - no complex layouts
"""

from fpdf import FPDF
import os

OUTPUT_DIR = "/data/.openclaw/workspace/welcome-frontend/frontend/public/pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_faq_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 15, 'FAQ-Vorlage fuer Hotels', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, '50+ haeufige Gaestefragen mit professionellen Antwortvorlagen', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    categories = [
        ("Anreise & Check-in", [
            ("Wie spaet kann ich anreisen?", "Der Check-in ist moeglich bis 22:00 Uhr."),
            ("Wo finde ich den Schluessel?", "Der Schluessel befindet sich im Keysafe an der Eingangstuer."),
            ("Gibt es Parkplaetze?", "Ja, wir haben kostenfreie Parkplaetze direkt vor dem Haus."),
            ("Kann ich frueher anreisen?", "Fruehcheck-in ist ab 12:00 Uhr moeglich."),
            ("Wann ist die Rezeption besetzt?", "Unsere Rezeption ist von 8:00 bis 20:00 Uhr besetzt."),
        ]),
        ("Unterkunft & Ausstattung", [
            ("Ist WLAN vorhanden?", "Ja, kostenloses WLAN ist im gesamten Haus verfuegbar."),
            ("Gibt es einen Fernseher?", "Ja, alle Zimmer sind mit einem Smart-TV ausgestattet."),
            ("Ist die Unterkunft barrierefrei?", "Ja, unsere Unterkunft ist barrierefrei zugaenglich."),
            ("Kann ich mit dem Haustier anreisen?", "Haustiere sind nach Absprache willkommen (10 Euro/Tag)."),
            ("Gibt es eine Kueche?", "Ja, alle Apartments haben eine voll ausgestattete Kueche."),
        ]),
        ("Lage & Umgebung", [
            ("Wie weit ist der naechste Supermarkt?", "Der naechste Supermarkt ist 5 Gehminuten entfernt."),
            ("Gibt es Restaurants in der Naehe?", "Ja, diverse Restaurants im Umkreis von 500m."),
            ("Wie komme ich zum Bahnhof?", "Der Bahnhof ist 10 Minuten zu Fuss."),
        ]),
        ("Check-out & Abreise", [
            ("Wann muss ich auschecken?", "Der Check-out ist bis 11:00 Uhr."),
            ("Kann ich spaeter auschecken?", "Spaetcheck-out ist nach Absprache moeglich (25 Euro)."),
            ("Kann ich mein Gepaeck lassen?", "Ja, Gepaeckaufbewahrung ist kostenlos."),
        ]),
        ("Zahlung & Service", [
            ("Welche Zahlungsarten werden akzeptiert?", "Bar, EC-Karte, Kreditkarte und PayPal."),
            ("Ist die Kurtaxe im Preis enthalten?", "Ja, die Kurtaxe ist im Gesamtpreis enthalten."),
            ("Gibt es Fruehstueck?", "Fruehstueck kann optional gebucht werden (15 Euro/Tag)."),
        ]),
    ]
    
    for category, questions in categories:
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, category, new_x="LMARGIN", new_y="NEXT")
        
        for q, a in questions:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 7, f"  Q: {q}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 7, f"  A: {a}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        
        pdf.ln(5)
    
    output_path = os.path.join(OUTPUT_DIR, "faq-vorlage-hotels.pdf")
    pdf.output(output_path)
    print(f"Created: {output_path}")


def create_upsell_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 15, 'Upsell-Texte Sammlung', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, 'Bewaehrte Formulierungen fuer Ihre Zusatzangebote', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    content = [
        ("FRUEHSTUECK", [
            "Titel: Reichhaltiges Fruehstueck",
            "Beschreibung: Starten Sie Ihren Tag mit einem frischen Fruehstueck",
            "Preis: 15 Euro pro Person/Tag",
        ]),
        ("FRUEH-/SPAETCHECK-IN/OUT", [
            "Fruhcheck-in: 15 Euro (ab 12:00 Uhr)",
            "Spaetcheck-out: 25 Euro (bis 14:00 Uhr)",
        ]),
        ("PARKEN", [
            "Titel: Sicherer Parkplatz",
            "Preis: 10 Euro/Tag",
        ]),
        ("WELLNESS", [
            "Private Sauna: 30 Euro (2 Stunden)",
            "Massage: 65 Euro (60 Minuten)",
        ]),
        ("TRANSFER", [
            "Bahnhof-Shuttle: 20 Euro",
            "Fahrradverleih: 12 Euro/Tag",
        ]),
    ]
    
    for cat, items in content:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, cat, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(50, 50, 50)
        for item in items:
            pdf.cell(0, 7, f"  {item}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
    
    # Tips page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 15, 'Upselling-Tipps', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    tips = [
        "Zeigen Sie Preise transparent an",
        "Nutzen Sie ansprechende Bilder",
        "Positionieren Sie Upsells zum richtigen Zeitpunkt",
        "Bieten Sie Pakete an",
        "Nutzen Sie Verknappung fuer beliebte Extras",
        "Personalisieren Sie Angebote",
        "Senden Sie Upsell-Angebote 3 Tage vor Anreise",
        "Fragen Sie bei Check-in nach Wuenschen",
    ]
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    for i, tip in enumerate(tips, 1):
        pdf.cell(0, 8, f"{i}. {tip}", new_x="LMARGIN", new_y="NEXT")
    
    output_path = os.path.join(OUTPUT_DIR, "upsell-texte-sammlung.pdf")
    pdf.output(output_path)
    print(f"Created: {output_path}")


def create_email_templates_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 15, 'Email Templates', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, 'Professionelle Email-Vorlagen fuer Gaestekommunikation', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Template 1
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '1. Buchungsbestaetigung', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(50, 50, 50)
    lines = [
        "Betreff: Ihre Buchungsbestaetigung - [Unterkunft]",
        "",
        "Sehr geehrte/r [Gaestename],",
        "",
        "vielen Dank fuer Ihre Buchung!",
        "",
        "Ihre Buchungsdetails:",
        "- Unterkunft: [Unterkunft Name]",
        "- Anreise: [Datum]",
        "- Abreise: [Datum]",
        "- Gaeste: [Anzahl]",
        "",
        "Check-in: ab 15:00 Uhr",
        "Check-out: bis 11:00 Uhr",
        "",
        "Wir freuen uns auf Ihren Besuch!",
    ]
    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Template 2
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '2. Willkommens-Email', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(50, 50, 50)
    lines = [
        "Betreff: Willkommen! Ihre Anreise steht bevor",
        "",
        "Sehr geehrte/r [Gaestename],",
        "",
        "morgen erwartet Sie [Unterkunft Name]!",
        "",
        "Check-in Informationen:",
        "- Keysafe-Code: [Code]",
        "- WLAN: [Name] / [Passwort]",
        "- Adresse: [Adresse]",
        "",
        "Ihre digitale Gaestemappe: [Link]",
    ]
    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Template 3
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, '3. Check-out Erinnerung', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(50, 50, 50)
    lines = [
        "Betreff: Ihr Check-out - Danke fuer Ihren Aufenthalt!",
        "",
        "Sehr geehrte/r [Gaestename],",
        "",
        "wir hoffen, Sie hatten einen angenehmen Aufenthalt!",
        "",
        "Check-out: heute bis 11:00 Uhr",
        "Schluesselabgabe: Keysafe",
        "",
        "Bewertung: [Link zur Bewertung]",
        "",
        "Vielen Dank!",
    ]
    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    
    output_path = os.path.join(OUTPUT_DIR, "email-templates.pdf")
    pdf.output(output_path)
    print(f"Created: {output_path}")


def create_onboarding_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 15, 'Welcome Link - Schnellstart Guide', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, 'Alles was Sie wissen muessen, um in 10 Minuten startklar zu sein.', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    steps = [
        ("Schritt 1: Account erstellen", [
            "1. Gehen Sie zu welcome-link.de/register",
            "2. Geben Sie Ihre E-Mail und Passwort ein",
            "3. Bestaetigen Sie Ihre E-Mail-Adresse",
        ]),
        ("Schritt 2: Erste Property anlegen", [
            "1. Klicken Sie im Dashboard auf 'Neue Property'",
            "2. Fuellen Sie die Basisinformationen aus",
            "3. Laden Sie Bilder hoch (min. 3 empfohlen)",
            "4. Speichern Sie",
        ]),
        ("Schritt 3: Gaestemappe konfigurieren", [
            "1. Oeffnen Sie Ihre Property",
            "2. Navigieren Sie zum Tab 'Gaestemappe'",
            "3. Fuellen Sie WLAN, Hausregeln, Check-in/out aus",
            "4. Vorschau anzeigen lassen",
        ]),
        ("Schritt 4: QR-Code generieren", [
            "1. Gehen Sie zum Tab 'QR-Code'",
            "2. Wahlen Sie 'Neuen QR-Code erstellen'",
            "3. Downloaden Sie den Code",
            "4. Platzieren Sie ihn an der Eingangstuer",
        ]),
        ("Schritt 5: Upselling aktivieren", [
            "1. Tab 'Extras' oeffnen",
            "2. Klicken Sie auf 'Neues Extra'",
            "3. Fuegen Sie Angebote hinzu",
            "4. Aktivieren Sie die Extras",
        ]),
    ]
    
    for title, items in steps:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(50, 50, 50)
        for item in items:
            pdf.cell(0, 7, f"  {item}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
    
    # Tips
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(242, 124, 44)
    pdf.cell(0, 10, 'Pro-Tipps', new_x="LMARGIN", new_y="NEXT")
    
    tips = [
        "Nutzen Sie die Airbnb-Import-Funktion fuer schnelleres Setup",
        "Laden Sie mindestens 5-10 Fotos hoch",
        "Aktualisieren Sie Ihre Gaestemappe saisonal",
        "Nutzen Sie die Analytics-Funktion",
    ]
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    for i, tip in enumerate(tips, 1):
        pdf.cell(0, 7, f"{i}. {tip}", new_x="LMARGIN", new_y="NEXT")
    
    output_path = os.path.join(OUTPUT_DIR, "onboarding-guide.pdf")
    pdf.output(output_path)
    print(f"Created: {output_path}")


if __name__ == "__main__":
    print("Generating PDFs...")
    create_faq_pdf()
    create_upsell_pdf()
    create_email_templates_pdf()
    create_onboarding_pdf()
    print("\nAll PDFs generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")