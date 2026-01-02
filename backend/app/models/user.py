"""
User model
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enum"""
    OWNER = "owner"
    MEMBER = "member"


class User(BaseModel):
    """User model - synced with Supabase Auth"""
    id: str
    email: str
    full_name: Optional[str] = None
    organization_id: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    avatar_url: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    def is_owner(self) -> bool:
        """Check if user is organization owner"""
        return self.role == UserRole.OWNER
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role == UserRole.OWNER

