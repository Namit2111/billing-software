"""
Product schemas
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ProductCreate(BaseModel):
    """Create product request"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    unit_price: float = Field(..., ge=0)
    unit: str = Field(default="unit", max_length=50)
    tax_rate: float = Field(default=0.0, ge=0, le=100)
    sku: Optional[str] = Field(None, max_length=50)


class ProductUpdate(BaseModel):
    """Update product request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    unit_price: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    sku: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product response"""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    unit_price: float
    unit: str
    tax_rate: float
    sku: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list item"""
    id: str
    name: str
    unit_price: float
    unit: str
    tax_rate: float
    is_active: bool
    
    class Config:
        from_attributes = True

