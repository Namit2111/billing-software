"""
Email service
"""
from typing import Dict, Any, Optional
import resend
from supabase import Client

from app.core.config import settings
from app.repositories.email_log import EmailLogRepository


class EmailService:
    """Service for sending emails"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.email_log_repo = EmailLogRepository(supabase)
        
        # Initialize Resend
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY
    
    async def send_invoice_email(
        self,
        organization_id: str,
        invoice: Dict[str, Any],
        recipient_email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        pdf_bytes: Optional[bytes] = None,
        sender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send invoice via email
        
        Args:
            organization_id: Organization UUID
            invoice: Invoice data
            recipient_email: Recipient email address
            subject: Email subject (optional, defaults to invoice subject)
            message: Custom message body
            pdf_bytes: PDF attachment bytes
            sender_name: Sender name for email
            
        Returns:
            Email log record
        """
        # Build default subject
        if not subject:
            subject = f"Invoice {invoice.get('invoice_number', '')} from {sender_name or settings.APP_NAME}"
        
        # Build default message
        if not message:
            message = self._build_default_message(invoice, sender_name)
        
        # Create email log
        log = await self.email_log_repo.create({
            "organization_id": organization_id,
            "invoice_id": invoice.get("id"),
            "recipient_email": recipient_email,
            "subject": subject,
            "body": message,
            "status": "pending"
        })
        
        try:
            # Prepare attachments
            attachments = []
            if pdf_bytes:
                import base64
                attachments.append({
                    "filename": f"invoice-{invoice.get('invoice_number', 'document')}.pdf",
                    "content": base64.b64encode(pdf_bytes).decode('utf-8'),
                    "type": "application/pdf"
                })
            
            # Send via Resend
            if settings.RESEND_API_KEY:
                params = {
                    "from": f"{sender_name or settings.APP_NAME} <{settings.FROM_EMAIL}>",
                    "to": [recipient_email],
                    "subject": subject,
                    "html": self._build_html_email(message, invoice),
                }
                
                if attachments:
                    params["attachments"] = attachments
                
                response = resend.Emails.send(params)
                
                # Update log with success
                await self.email_log_repo.update_status(
                    log["id"],
                    "sent",
                )
                log["status"] = "sent"
                log["provider_id"] = response.get("id")
            else:
                # No API key - mark as sent for development
                await self.email_log_repo.update_status(log["id"], "sent")
                log["status"] = "sent"
            
        except Exception as e:
            # Update log with error
            await self.email_log_repo.update_status(
                log["id"],
                "failed",
                str(e)
            )
            log["status"] = "failed"
            log["error_message"] = str(e)
        
        return log
    
    def _build_default_message(
        self,
        invoice: Dict[str, Any],
        sender_name: Optional[str] = None
    ) -> str:
        """Build default email message"""
        invoice_number = invoice.get('invoice_number', '')
        total = invoice.get('total', 0)
        currency = invoice.get('currency', 'USD')
        due_date = invoice.get('due_date', '')
        
        return f"""
Hello,

Please find attached invoice {invoice_number} for {self._format_currency(total, currency)}.

Due Date: {due_date}

If you have any questions about this invoice, please don't hesitate to reach out.

Thank you for your business!

Best regards,
{sender_name or settings.APP_NAME}
        """.strip()
    
    def _build_html_email(
        self,
        message: str,
        invoice: Dict[str, Any]
    ) -> str:
        """Build HTML email template"""
        invoice_number = invoice.get('invoice_number', '')
        total = invoice.get('total', 0)
        currency = invoice.get('currency', 'USD')
        due_date = invoice.get('due_date', '')
        status = invoice.get('status', 'sent')
        
        # Convert message to HTML
        html_message = message.replace('\n', '<br>')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice {invoice_number}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #0F172A; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">Invoice {invoice_number}</h1>
    </div>
    
    <div style="background: #F8FAFC; padding: 30px; border: 1px solid #E2E8F0; border-top: none;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="background: white; padding: 15px 20px; border-radius: 8px; text-align: center; flex: 1; margin-right: 10px; border: 1px solid #E2E8F0;">
                <div style="font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">Amount Due</div>
                <div style="font-size: 24px; font-weight: bold; color: #2563EB;">{self._format_currency(total, currency)}</div>
            </div>
            <div style="background: white; padding: 15px 20px; border-radius: 8px; text-align: center; flex: 1; margin-left: 10px; border: 1px solid #E2E8F0;">
                <div style="font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">Due Date</div>
                <div style="font-size: 18px; font-weight: 600; color: #0F172A;">{due_date}</div>
            </div>
        </div>
        
        <div style="background: white; padding: 25px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <p style="margin: 0; color: #334155;">
                {html_message}
            </p>
        </div>
    </div>
    
    <div style="background: #0F172A; color: #94A3B8; padding: 20px; border-radius: 0 0 12px 12px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">This invoice was sent via {settings.APP_NAME}</p>
    </div>
</body>
</html>
        """
    
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
    
    async def get_invoice_emails(
        self,
        invoice_id: str
    ) -> list:
        """Get all emails sent for an invoice"""
        return await self.email_log_repo.get_by_invoice(invoice_id)
    
    async def get_recent_emails(
        self,
        organization_id: str,
        limit: int = 20
    ) -> list:
        """Get recent emails for organization"""
        return await self.email_log_repo.get_recent(organization_id, limit)

