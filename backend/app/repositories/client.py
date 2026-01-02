"""
Client repository
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    """Repository for client operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "clients")
    
    async def search(
        self,
        organization_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search clients by name, email, or company name
        
        Args:
            organization_id: Organization UUID
            query: Search query
            limit: Max results
            
        Returns:
            List of matching clients
        """
        # Use ilike for case-insensitive search
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .or_(f"name.ilike.%{query}%,email.ilike.%{query}%,company_name.ilike.%{query}%")\
            .limit(limit)\
            .execute()
        
        return response.data or []
    
    async def get_active(
        self,
        organization_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all active clients for an organization"""
        return await self.get_all(
            organization_id=organization_id,
            filters={"is_active": True},
            order_by="name",
            ascending=True,
            limit=limit,
            offset=offset
        )
    
    async def get_with_invoice_count(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get clients with their invoice counts"""
        # Get clients
        clients = await self.get_active(organization_id)
        
        # Get invoice counts per client
        for client in clients:
            response = self.supabase.table("invoices")\
                .select("id", count="exact")\
                .eq("client_id", client["id"])\
                .execute()
            client["invoice_count"] = response.count or 0
        
        return clients
    
    async def get_by_email(
        self,
        organization_id: str,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """Get client by email within organization"""
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("organization_id", organization_id)\
                .eq("email", email)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None

