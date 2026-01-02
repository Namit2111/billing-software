"""
Tax schemas
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TaxCreate(BaseModel):
    """Create tax rate request"""
    name: str = Field(..., min_length=1, max_length=100)
    rate: float = Field(..., ge=0, le=100)
    description: Optional[str] = None
    is_default: bool = False


class TaxUpdate(BaseModel):
    """Update tax rate request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rate: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class TaxResponse(BaseModel):
    """Tax rate response"""
    id: str
    organization_id: str
    name: str
    rate: float
    description: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

