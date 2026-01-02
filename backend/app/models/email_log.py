"""
Email log model
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class EmailLog(BaseModel):
    """Email sending log"""
    id: str
    organization_id: str
    invoice_id: Optional[str] = None
    recipient_email: str
    subject: str
    body: Optional[str] = None
    status: EmailStatus = EmailStatus.PENDING
    provider_id: Optional[str] = None  # Email provider message ID
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True

