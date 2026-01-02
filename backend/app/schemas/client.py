"""
Client schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ClientCreate(BaseModel):
    """Create client request"""
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="US", max_length=2)
    tax_id: Optional[str] = Field(None, max_length=50)
    currency: str = Field(default="USD", max_length=3)
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    """Update client request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    tax_id: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(BaseModel):
    """Client response"""
    id: str
    organization_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    company_name: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: str
    tax_id: Optional[str]
    currency: str
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Client list item (simplified)"""
    id: str
    name: str
    email: Optional[str]
    company_name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

