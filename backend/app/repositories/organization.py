"""
Organization repository
"""
from typing import Optional, Dict, Any
from supabase import Client

from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository):
    """Repository for organization operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "organizations")
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", id).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization"""
        if "id" not in data:
            data["id"] = self._generate_id()
        if "created_at" not in data:
            data["created_at"] = self._get_timestamp()
        if "updated_at" not in data:
            data["updated_at"] = self._get_timestamp()
        
        # Set defaults
        data.setdefault("invoice_prefix", "INV")
        data.setdefault("invoice_next_number", 1)
        data.setdefault("default_tax_rate", 0.0)
        data.setdefault("default_payment_terms", 30)
        data.setdefault("currency", "USD")
        data.setdefault("country", "US")
        
        response = self.supabase.table(self.table_name).insert(data).execute()
        return response.data[0] if response.data else None
    
    async def increment_invoice_number(self, id: str) -> int:
        """
        Increment and return the next invoice number
        
        Args:
            id: Organization UUID
            
        Returns:
            The new invoice number
        """
        # Get current number
        org = await self.get_by_id(id)
        if not org:
            return 1
        
        current_number = org.get("invoice_next_number", 1)
        new_number = current_number + 1
        
        # Update the number
        await self.update(id, {"invoice_next_number": new_number})
        
        return current_number
    
    async def get_next_invoice_number(self, id: str) -> str:
        """
        Get the formatted next invoice number
        
        Args:
            id: Organization UUID
            
        Returns:
            Formatted invoice number (e.g., "INV-0001")
        """
        org = await self.get_by_id(id)
        if not org:
            return "INV-0001"
        
        prefix = org.get("invoice_prefix", "INV")
        number = org.get("invoice_next_number", 1)
        
        return f"{prefix}-{str(number).zfill(4)}"
    
    async def update_logo(self, id: str, logo_url: str) -> Optional[Dict[str, Any]]:
        """Update organization logo"""
        return await self.update(id, {"logo_url": logo_url})

