"""
Tax model
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Tax(BaseModel):
    """Tax rate configuration"""
    id: str
    organization_id: str
    name: str
    rate: float
    description: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    def format_rate(self) -> str:
        """Format rate as percentage string"""
        return f"{self.rate}%"

