"""
Invoice schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status enum"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceItemCreate(BaseModel):
    """Create invoice item request"""
    product_id: Optional[str] = None
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(..., ge=0)
    tax_rate: float = Field(default=0.0, ge=0, le=100)
    discount_percent: float = Field(default=0.0, ge=0, le=100)


class InvoiceItemUpdate(BaseModel):
    """Update invoice item request"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)


class InvoiceItemResponse(BaseModel):
    """Invoice item response"""
    id: str
    invoice_id: str
    product_id: Optional[str]
    description: str
    quantity: float
    unit_price: float
    tax_rate: float
    discount_percent: float
    subtotal: float
    tax_amount: float
    total: float
    sort_order: int
    
    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    """Create invoice request"""
    client_id: str
    issue_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = None
    currency: str = Field(default="USD", max_length=3)
    notes: Optional[str] = None
    terms: Optional[str] = None
    footer: Optional[str] = None
    items: List[InvoiceItemCreate] = Field(default_factory=list)


class InvoiceUpdate(BaseModel):
    """Update invoice request"""
    client_id: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    footer: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    organization_id: str
    client_id: str
    invoice_number: str
    status: InvoiceStatus
    issue_date: date
    due_date: date
    currency: str
    subtotal: float
    tax_total: float
    discount_total: float
    total: float
    amount_paid: float
    balance_due: float
    notes: Optional[str]
    terms: Optional[str]
    footer: Optional[str]
    pdf_url: Optional[str]
    sent_at: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []
    client: Optional[dict] = None
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Invoice list item"""
    id: str
    invoice_number: str
    client_name: str
    status: InvoiceStatus
    issue_date: date
    due_date: date
    total: float
    balance_due: float
    currency: str
    
    class Config:
        from_attributes = True


class MarkPaidRequest(BaseModel):
    """Mark invoice as paid request"""
    amount_paid: Optional[float] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None


class SendInvoiceRequest(BaseModel):
    """Send invoice via email request"""
    recipient_email: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    attach_pdf: bool = True

