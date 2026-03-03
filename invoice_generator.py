"""
PDF Invoice Generator for Welcome Link
Uses reportlab for PDF generation
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from io import BytesIO

# Colors
BRAND_ORANGE = colors.HexColor('#f97316')
BRAND_AMBER = colors.HexColor('#f59e0b')
DARK_GRAY = colors.HexColor('#1f2937')
MEDIUM_GRAY = colors.HexColor('#6b7280')
LIGHT_GRAY = colors.HexColor('#f3f4f6')
WHITE = colors.white


class InvoiceGenerator:
    def __init__(self, brand_color=BRAND_ORANGE):
        self.brand_color = brand_color
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            fontSize=24,
            leading=28,
            textColor=DARK_GRAY,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='InvoiceSubtitle',
            fontSize=12,
            leading=16,
            textColor=MEDIUM_GRAY,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='InvoiceLabel',
            fontSize=10,
            leading=12,
            textColor=MEDIUM_GRAY,
            spaceAfter=2
        ))
        self.styles.add(ParagraphStyle(
            name='InvoiceValue',
            fontSize=12,
            leading=16,
            textColor=DARK_GRAY,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='InvoiceFooter',
            fontSize=9,
            leading=12,
            textColor=MEDIUM_GRAY,
            alignment=1  # Center
        ))
    
    def generate(self, invoice_data: dict) -> bytes:
        """
        Generate PDF invoice
        
        Args:
            invoice_data: dict with keys:
                - invoice_number: str
                - invoice_date: datetime
                - due_date: datetime
                - host_name: str
                - host_address: str
                - host_email: str
                - guest_name: str
                - guest_email: str
                - property_name: str
                - property_address: str
                - items: list of {name, description, quantity, price, total}
                - subtotal: float
                - tax: float
                - total: float
                - payment_method: str
                - payment_status: str
        
        Returns:
            PDF as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Header with logo
        elements.extend(self._build_header(invoice_data))
        
        # Addresses
        elements.extend(self._build_addresses(invoice_data))
        
        # Invoice details
        elements.extend(self._build_details(invoice_data))
        
        # Items table
        elements.extend(self._build_items_table(invoice_data))
        
        # Totals
        elements.extend(self._build_totals(invoice_data))
        
        # Payment info
        elements.extend(self._build_payment_info(invoice_data))
        
        # Footer
        elements.extend(self._build_footer(invoice_data))
        
        # Build PDF
        doc.build(elements)
        
        return buffer.getvalue()
    
    def _build_header(self, data):
        """Build invoice header"""
        elements = []
        
        # Brand
        elements.append(Paragraph(
            '<font color="#f97316" size="28"><b>Welcome</font><font color="#f59e0b" size="28">Link</b></font>',
            self.styles['InvoiceTitle']
        ))
        
        elements.append(Paragraph(
            'Digitale Gästemappe für Ferienunterkünfte',
            self.styles['InvoiceSubtitle']
        ))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_addresses(self, data):
        """Build from/to addresses"""
        elements = []
        
        # Create address table
        address_data = [
            ['VON:', 'AN:'],
            [
                Paragraph(data.get('host_name', ''), self.styles['InvoiceValue']),
                Paragraph(data.get('guest_name', ''), self.styles['InvoiceValue'])
            ],
            [
                Paragraph(data.get('host_address', ''), self.styles['InvoiceValue']),
                Paragraph(data.get('guest_email', ''), self.styles['InvoiceValue'])
            ],
        ]
        
        address_table = Table(address_data, colWidths=[8*cm, 8*cm])
        address_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), MEDIUM_GRAY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(address_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_details(self, data):
        """Build invoice details section"""
        elements = []
        
        elements.append(Paragraph(
            '<b>RECHNUNG</b>',
            self.styles['InvoiceTitle']
        ))
        
        # Invoice number and dates
        details_data = [
            ['Rechnungsnummer:', data.get('invoice_number', 'WL-2024-0001')],
            ['Rechnungsdatum:', data.get('invoice_date', datetime.now()).strftime('%d.%m.%Y')],
            ['Fälligkeitsdatum:', data.get('due_date', datetime.now()).strftime('%d.%m.%Y')],
            ['Unterkunft:', data.get('property_name', '')],
        ]
        
        details_table = Table(details_data, colWidths=[5*cm, 10*cm])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), MEDIUM_GRAY),
            ('TEXTCOLOR', (1, 0), (1, -1), DARK_GRAY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_items_table(self, data):
        """Build items table"""
        elements = []
        
        # Header
        header = ['Beschreibung', 'Menge', 'Einzelpreis', 'Gesamt']
        
        # Items
        items = data.get('items', [])
        rows = [header]
        
        for item in items:
            rows.append([
                f"{item.get('name', '')}\n{item.get('description', '')}",
                str(item.get('quantity', 1)),
                f"€{item.get('price', 0):.2f}",
                f"€{item.get('total', 0):.2f}"
            ])
        
        # Create table
        items_table = Table(rows, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), DARK_GRAY),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            
            # Grid
            ('LINEBELOW', (0, 0), (-1, 0), 1, WHITE),
            ('LINEBELOW', (0, -1), (-1, -1), 1, DARK_GRAY),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_totals(self, data):
        """Build totals section"""
        elements = []
        
        subtotal = data.get('subtotal', 0)
        tax = data.get('tax', 0)
        total = data.get('total', 0)
        
        totals_data = [
            ['', '', 'Zwischensumme:', f'€{subtotal:.2f}'],
            ['', '', 'MwSt (19%):', f'€{tax:.2f}'],
            ['', '', 'Gesamtbetrag:', f'€{total:.2f}'],
        ]
        
        totals_table = Table(totals_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, 1), DARK_GRAY),
            ('TEXTCOLOR', (0, 2), (-1, 2), self.brand_color),
            ('FONTSIZE', (0, 2), (-1, 2), 14),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (2, 2), (-1, 2), 1, DARK_GRAY),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_payment_info(self, data):
        """Build payment information"""
        elements = []
        
        payment_method = data.get('payment_method', 'N/A')
        payment_status = data.get('payment_status', 'ausstehend')
        
        status_color = colors.HexColor('#10b981') if payment_status == 'bezahlt' else BRAND_ORANGE
        
        elements.append(Paragraph(
            '<b>Zahlungsinformationen</b>',
            self.styles['InvoiceValue']
        ))
        
        payment_data = [
            ['Zahlungsmethode:', payment_method],
            ['Status:', payment_status],
        ]
        
        payment_table = Table(payment_data, colWidths=[5*cm, 10*cm])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), MEDIUM_GRAY),
            ('TEXTCOLOR', (1, 0), (1, 0), DARK_GRAY),
            ('TEXTCOLOR', (1, 1), (1, 1), status_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(payment_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_footer(self, data):
        """Build invoice footer"""
        elements = []
        
        footer_text = """
        <b>SEC GmbH</b> · Musterstraße 1 · 12345 Musterstadt<br/>
        E-Mail: info@welcome-link.de · Web: www.welcome-link.de<br/>
        <br/>
        Bankverbindung: IBAN DE00 0000 0000 0000 0000 · BIC: XXXXXXX<br/>
        USt-Id: DE000000000 · Handelsregister: HRB 000000
        """
        
        elements.append(Paragraph(footer_text, self.styles['InvoiceFooter']))
        
        return elements


# Convenience function
def generate_invoice(invoice_data: dict) -> bytes:
    """Generate invoice PDF from data"""
    generator = InvoiceGenerator()
    return generator.generate(invoice_data)