"""
Product repository
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for product/service operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "products")
    
    async def search(
        self,
        organization_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search products by name or SKU
        
        Args:
            organization_id: Organization UUID
            query: Search query
            limit: Max results
            
        Returns:
            List of matching products
        """
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .or_(f"name.ilike.%{query}%,sku.ilike.%{query}%")\
            .limit(limit)\
            .execute()
        
        return response.data or []
    
    async def get_active(
        self,
        organization_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all active products for an organization"""
        return await self.get_all(
            organization_id=organization_id,
            filters={"is_active": True},
            order_by="name",
            ascending=True,
            limit=limit,
            offset=offset
        )
    
    async def get_by_sku(
        self,
        organization_id: str,
        sku: str
    ) -> Optional[Dict[str, Any]]:
        """Get product by SKU within organization"""
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("organization_id", organization_id)\
                .eq("sku", sku)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None

