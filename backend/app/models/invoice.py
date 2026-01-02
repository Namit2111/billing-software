"""
Invoice and InvoiceItem models
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


class InvoiceItem(BaseModel):
    """Invoice line item"""
    id: str
    invoice_id: str
    product_id: Optional[str] = None
    description: str
    quantity: float = 1.0
    unit_price: float
    tax_rate: float = 0.0
    discount_percent: float = 0.0
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    def get_subtotal(self) -> float:
        """Calculate line item subtotal before tax"""
        base = self.quantity * self.unit_price
        discount = base * (self.discount_percent / 100)
        return base - discount
    
    def get_tax_amount(self) -> float:
        """Calculate tax amount for line item"""
        return self.get_subtotal() * (self.tax_rate / 100)
    
    def get_total(self) -> float:
        """Calculate line item total including tax"""
        return self.get_subtotal() + self.get_tax_amount()


class Invoice(BaseModel):
    """Invoice model"""
    id: str
    organization_id: str
    client_id: str
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: date
    due_date: date
    currency: str = "USD"
    subtotal: float = 0.0
    tax_total: float = 0.0
    discount_total: float = 0.0
    total: float = 0.0
    amount_paid: float = 0.0
    notes: Optional[str] = None
    terms: Optional[str] = None
    footer: Optional[str] = None
    pdf_url: Optional[str] = None
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    # Related data (not stored in DB, populated by joins)
    items: List[InvoiceItem] = Field(default_factory=list)
    client: Optional[dict] = None
    
    class Config:
        from_attributes = True
    
    def get_balance_due(self) -> float:
        """Calculate remaining balance due"""
        return self.total - self.amount_paid
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if self.status == InvoiceStatus.PAID:
            return False
        return date.today() > self.due_date
    
    def is_editable(self) -> bool:
        """Check if invoice can be edited"""
        return self.status == InvoiceStatus.DRAFT
    
    def calculate_totals(self) -> None:
        """Recalculate invoice totals from line items"""
        self.subtotal = sum(item.get_subtotal() for item in self.items)
        self.tax_total = sum(item.get_tax_amount() for item in self.items)
        self.total = self.subtotal + self.tax_total

