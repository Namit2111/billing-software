"""
PDF generation service
"""
from typing import Dict, Any, Optional
from datetime import date
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from supabase import Client

from app.core.config import settings


class PDFService:
    """Service for PDF invoice generation"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563EB'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#64748B'),
            spaceBefore=12,
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        ))
        
        self.styles.add(ParagraphStyle(
            name='TotalLabel',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0F172A')
        ))
        
        self.styles.add(ParagraphStyle(
            name='TotalAmount',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2563EB'),
            alignment=TA_RIGHT
        ))
    
    async def generate_invoice_pdf(
        self,
        invoice: Dict[str, Any],
        organization: Dict[str, Any]
    ) -> bytes:
        """
        Generate PDF for an invoice
        
        Args:
            invoice: Invoice data with items
            organization: Organization data
            
        Returns:
            PDF file bytes
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # Header section
        story.extend(self._build_header(invoice, organization))
        
        # Bill To section
        story.extend(self._build_bill_to(invoice))
        
        # Line items table
        story.extend(self._build_items_table(invoice))
        
        # Totals section
        story.extend(self._build_totals(invoice))
        
        # Notes and Terms
        story.extend(self._build_footer(invoice))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_header(
        self,
        invoice: Dict[str, Any],
        organization: Dict[str, Any]
    ) -> list:
        """Build PDF header section"""
        elements = []
        
        # Company name and invoice title row
        header_data = [
            [
                Paragraph(organization.get('name', 'Company'), self.styles['CompanyName']),
                Paragraph('INVOICE', self.styles['InvoiceTitle'])
            ]
        ]
        
        header_table = Table(header_data, colWidths=[300, 170])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        # Company details and invoice info
        company_info = []
        if organization.get('address_line1'):
            company_info.append(organization['address_line1'])
        if organization.get('address_line2'):
            company_info.append(organization['address_line2'])
        
        city_state = []
        if organization.get('city'):
            city_state.append(organization['city'])
        if organization.get('state'):
            city_state.append(organization['state'])
        if organization.get('postal_code'):
            city_state.append(organization['postal_code'])
        if city_state:
            company_info.append(', '.join(city_state))
        
        if organization.get('email'):
            company_info.append(organization['email'])
        if organization.get('phone'):
            company_info.append(organization['phone'])
        
        company_text = '<br/>'.join(company_info) if company_info else ''
        
        # Invoice details
        invoice_info = [
            f"<b>Invoice #:</b> {invoice.get('invoice_number', '')}",
            f"<b>Issue Date:</b> {self._format_date(invoice.get('issue_date'))}",
            f"<b>Due Date:</b> {self._format_date(invoice.get('due_date'))}",
        ]
        
        if invoice.get('status') == 'paid':
            invoice_info.append("<b>Status:</b> <font color='green'>PAID</font>")
        
        invoice_text = '<br/>'.join(invoice_info)
        
        info_data = [
            [
                Paragraph(company_text, self.styles['BodyText']),
                Paragraph(invoice_text, self.styles['BodyText'])
            ]
        ]
        
        info_table = Table(info_data, colWidths=[300, 170])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_bill_to(self, invoice: Dict[str, Any]) -> list:
        """Build Bill To section"""
        elements = []
        
        client = invoice.get('client', {})
        
        elements.append(Paragraph('BILL TO', self.styles['SectionHeader']))
        
        client_info = []
        if client.get('company_name'):
            client_info.append(f"<b>{client['company_name']}</b>")
        if client.get('name'):
            client_info.append(client['name'])
        if client.get('address_line1'):
            client_info.append(client['address_line1'])
        if client.get('address_line2'):
            client_info.append(client['address_line2'])
        
        city_state = []
        if client.get('city'):
            city_state.append(client['city'])
        if client.get('state'):
            city_state.append(client['state'])
        if client.get('postal_code'):
            city_state.append(client['postal_code'])
        if city_state:
            client_info.append(', '.join(city_state))
        
        if client.get('email'):
            client_info.append(client['email'])
        
        if client.get('tax_id'):
            client_info.append(f"Tax ID: {client['tax_id']}")
        
        client_text = '<br/>'.join(client_info) if client_info else 'N/A'
        elements.append(Paragraph(client_text, self.styles['BodyText']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_items_table(self, invoice: Dict[str, Any]) -> list:
        """Build line items table"""
        elements = []
        
        # Table headers
        headers = ['Description', 'Qty', 'Unit Price', 'Tax', 'Amount']
        
        # Table data
        items = invoice.get('items', [])
        currency = invoice.get('currency', 'USD')
        
        table_data = [headers]
        
        for item in items:
            qty = item.get('quantity', 1)
            unit_price = item.get('unit_price', 0)
            tax_rate = item.get('tax_rate', 0)
            
            subtotal = qty * unit_price
            discount = subtotal * (item.get('discount_percent', 0) / 100)
            taxable = subtotal - discount
            tax = taxable * (tax_rate / 100)
            total = taxable + tax
            
            row = [
                Paragraph(item.get('description', ''), self.styles['BodyText']),
                str(qty),
                self._format_currency(unit_price, currency),
                f"{tax_rate}%",
                self._format_currency(total, currency)
            ]
            table_data.append(row)
        
        # Create table
        col_widths = [220, 50, 80, 50, 80]
        items_table = Table(table_data, colWidths=col_widths)
        
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Alignment
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Grid
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#E2E8F0')),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_totals(self, invoice: Dict[str, Any]) -> list:
        """Build totals section"""
        elements = []
        
        currency = invoice.get('currency', 'USD')
        subtotal = invoice.get('subtotal', 0)
        tax_total = invoice.get('tax_total', 0)
        discount_total = invoice.get('discount_total', 0)
        total = invoice.get('total', 0)
        amount_paid = invoice.get('amount_paid', 0)
        balance_due = total - amount_paid
        
        totals_data = []
        
        totals_data.append(['Subtotal:', self._format_currency(subtotal, currency)])
        
        if discount_total > 0:
            totals_data.append(['Discount:', f"-{self._format_currency(discount_total, currency)}"])
        
        if tax_total > 0:
            totals_data.append(['Tax:', self._format_currency(tax_total, currency)])
        
        totals_data.append(['', ''])
        totals_data.append([
            Paragraph('<b>Total:</b>', self.styles['TotalLabel']),
            Paragraph(f"<b>{self._format_currency(total, currency)}</b>", self.styles['TotalAmount'])
        ])
        
        if amount_paid > 0:
            totals_data.append(['Amount Paid:', self._format_currency(amount_paid, currency)])
            totals_data.append([
                Paragraph('<b>Balance Due:</b>', self.styles['TotalLabel']),
                Paragraph(f"<b>{self._format_currency(balance_due, currency)}</b>", self.styles['TotalAmount'])
            ])
        
        # Right-align totals
        totals_table = Table(totals_data, colWidths=[350, 130])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#2563EB')),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_footer(self, invoice: Dict[str, Any]) -> list:
        """Build notes and terms footer"""
        elements = []
        
        if invoice.get('notes'):
            elements.append(Paragraph('Notes', self.styles['SectionHeader']))
            elements.append(Paragraph(invoice['notes'], self.styles['BodyText']))
            elements.append(Spacer(1, 15))
        
        if invoice.get('terms'):
            elements.append(Paragraph('Terms & Conditions', self.styles['SectionHeader']))
            elements.append(Paragraph(invoice['terms'], self.styles['BodyText']))
            elements.append(Spacer(1, 15))
        
        if invoice.get('footer'):
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(invoice['footer'], self.styles['BodyText']))
        
        return elements
    
    def _format_date(self, date_value) -> str:
        """Format date for display"""
        if not date_value:
            return ''
        if isinstance(date_value, str):
            try:
                date_value = date.fromisoformat(date_value)
            except:
                return date_value
        return date_value.strftime('%B %d, %Y')
    
    def _format_currency(self, amount: float, currency: str = 'USD') -> str:
        """Format amount as currency"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'JPY': '¥',
            'CAD': 'C$',
            'AUD': 'A$'
        }
        symbol = symbols.get(currency, currency + ' ')
        return f"{symbol}{amount:,.2f}"
    
    async def save_to_storage(
        self,
        pdf_bytes: bytes,
        invoice_id: str,
        organization_id: str
    ) -> str:
        """
        Save PDF to Supabase Storage
        
        Args:
            pdf_bytes: PDF file bytes
            invoice_id: Invoice UUID
            organization_id: Organization UUID
            
        Returns:
            Public URL of the saved PDF
        """
        storage_path = f"{organization_id}/{invoice_id}.pdf"
        
        # Upload to storage
        self.supabase.storage.from_(settings.STORAGE_BUCKET).upload(
            storage_path,
            pdf_bytes,
            {"content-type": "application/pdf"}
        )
        
        # Get public URL
        url = self.supabase.storage.from_(settings.STORAGE_BUCKET).get_public_url(storage_path)
        
        return url

