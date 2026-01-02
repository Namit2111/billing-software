"""
Tax repository
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class TaxRepository(BaseRepository):
    """Repository for tax rate operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "taxes")
    
    async def get_active(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get all active tax rates for an organization"""
        return await self.get_all(
            organization_id=organization_id,
            filters={"is_active": True},
            order_by="name",
            ascending=True
        )
    
    async def get_default(
        self,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get default tax rate for an organization"""
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("organization_id", organization_id)\
                .eq("is_default", True)\
                .eq("is_active", True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def set_default(
        self,
        organization_id: str,
        tax_id: str
    ) -> Optional[Dict[str, Any]]:
        """Set a tax rate as the default (unsets others)"""
        # Unset current default
        self.supabase.table(self.table_name)\
            .update({"is_default": False})\
            .eq("organization_id", organization_id)\
            .eq("is_default", True)\
            .execute()
        
        # Set new default
        return await self.update(tax_id, {"is_default": True})
    
    async def get_by_name(
        self,
        organization_id: str,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """Get tax rate by name"""
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("organization_id", organization_id)\
                .eq("name", name)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None

