"""
Organization model
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Organization(BaseModel):
    """Organization/Company model"""
    id: str
    name: str
    logo_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "US"
    currency: str = "USD"
    invoice_prefix: str = "INV"
    invoice_next_number: int = 1
    default_tax_rate: float = 0.0
    default_payment_terms: int = 30  # days
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    def get_next_invoice_number(self) -> str:
        """Generate next invoice number"""
        return f"{self.invoice_prefix}-{str(self.invoice_next_number).zfill(4)}"
    
    def get_full_address(self) -> str:
        """Get formatted full address"""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city or self.state or self.postal_code:
            city_line = ", ".join(filter(None, [self.city, self.state, self.postal_code]))
            parts.append(city_line)
        if self.country:
            parts.append(self.country)
        return "\n".join(parts)

