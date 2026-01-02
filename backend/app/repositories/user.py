"""
User repository
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "users")
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", id).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("email", email).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user record"""
        if "created_at" not in data:
            data["created_at"] = self._get_timestamp()
        if "updated_at" not in data:
            data["updated_at"] = self._get_timestamp()
        
        # Set defaults
        data.setdefault("role", "member")
        data.setdefault("is_active", True)
        
        response = self.supabase.table(self.table_name).insert(data).execute()
        return response.data[0] if response.data else None
    
    async def get_by_organization(
        self,
        organization_id: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all users in an organization"""
        query = self.supabase.table(self.table_name).select("*").eq("organization_id", organization_id)
        
        if not include_inactive:
            query = query.eq("is_active", True)
        
        response = query.order("created_at", desc=False).execute()
        return response.data or []
    
    async def update_organization(
        self,
        user_id: str,
        organization_id: str,
        role: str = "member"
    ) -> Optional[Dict[str, Any]]:
        """Associate user with an organization"""
        return await self.update(user_id, {
            "organization_id": organization_id,
            "role": role
        })
    
    async def update_last_login(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Update user's last login timestamp"""
        return await self.update(user_id, {"last_login": self._get_timestamp()})
    
    async def deactivate(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Deactivate a user"""
        return await self.update(user_id, {"is_active": False})
    
    async def change_role(
        self,
        user_id: str,
        new_role: str
    ) -> Optional[Dict[str, Any]]:
        """Change user's role"""
        return await self.update(user_id, {"role": new_role})

