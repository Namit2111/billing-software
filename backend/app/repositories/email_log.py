"""
Email log repository
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class EmailLogRepository(BaseRepository):
    """Repository for email log operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "email_logs")
    
    async def get_by_invoice(self, invoice_id: str) -> List[Dict[str, Any]]:
        """Get all email logs for an invoice"""
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("invoice_id", invoice_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data or []
    
    async def get_recent(
        self,
        organization_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent email logs"""
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data or []
    
    async def update_status(
        self,
        id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update email status"""
        data = {"status": status}
        if error_message:
            data["error_message"] = error_message
        if status == "sent":
            data["sent_at"] = self._get_timestamp()
        return await self.update(id, data)

