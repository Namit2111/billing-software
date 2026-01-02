"""
Organization schemas
"""
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class OrganizationCreate(BaseModel):
    """Create organization request"""
    name: str = Field(..., min_length=2, max_length=200)
    currency: str = Field(default="USD", max_length=3)
    country: str = Field(default="US", max_length=2)


class OrganizationUpdate(BaseModel):
    """Update organization request"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    logo_url: Optional[str] = None
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    currency: Optional[str] = Field(None, max_length=3)
    invoice_prefix: Optional[str] = Field(None, max_length=10)
    default_tax_rate: Optional[float] = Field(None, ge=0, le=100)
    default_payment_terms: Optional[int] = Field(None, ge=0, le=365)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    website: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=50)


class OrganizationResponse(BaseModel):
    """Organization response"""
    id: str
    name: str
    logo_url: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: str
    currency: str
    invoice_prefix: str
    invoice_next_number: int
    default_tax_rate: float
    default_payment_terms: int
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    tax_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceSettingsUpdate(BaseModel):
    """Update invoice settings"""
    invoice_prefix: Optional[str] = Field(None, max_length=10)
    default_tax_rate: Optional[float] = Field(None, ge=0, le=100)
    default_payment_terms: Optional[int] = Field(None, ge=0, le=365)

