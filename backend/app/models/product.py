"""
Product/Service model
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class Product(BaseModel):
    """Product or Service catalog item"""
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    unit_price: float
    unit: str = "unit"  # e.g., hour, piece, service
    tax_rate: float = 0.0
    sku: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    def get_price_with_tax(self) -> float:
        """Calculate price including tax"""
        return self.unit_price * (1 + self.tax_rate / 100)

