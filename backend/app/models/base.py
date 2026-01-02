"""
Base model with common fields
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class BaseDBModel(BaseModel):
    """Base model with common database fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class AuditableModel(BaseDBModel):
    """Model with audit fields"""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

