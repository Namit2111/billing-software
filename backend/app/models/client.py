"""
Client model
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Client(BaseModel):
    """Client/Customer model"""
    id: str
    organization_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "US"
    tax_id: Optional[str] = None
    currency: str = "USD"
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    def get_display_name(self) -> str:
        """Get display name (company name or contact name)"""
        return self.company_name or self.name
    
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

