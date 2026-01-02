"""
Tax service
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.tax import TaxRepository
from app.core.exceptions import NotFoundError, ConflictError


class TaxService:
    """Service for tax rate operations"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.tax_repo = TaxRepository(supabase)
    
    async def create(
        self,
        organization_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new tax rate"""
        # Check for duplicate name
        existing = await self.tax_repo.get_by_name(organization_id, data["name"])
        if existing:
            raise ConflictError(f"Tax rate '{data['name']}' already exists")
        
        data["organization_id"] = organization_id
        
        # If this is set as default, unset others
        if data.get("is_default"):
            await self.tax_repo.set_default(organization_id, "")
        
        return await self.tax_repo.create(data)
    
    async def get(
        self,
        tax_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get tax rate by ID"""
        tax = await self.tax_repo.get_by_id(tax_id)
        
        if not tax or tax.get("organization_id") != organization_id:
            raise NotFoundError("Tax rate", tax_id)
        
        return tax
    
    async def update(
        self,
        tax_id: str,
        organization_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update tax rate"""
        tax = await self.get(tax_id, organization_id)
        
        # Check for duplicate name if changing
        if data.get("name") and data["name"] != tax.get("name"):
            existing = await self.tax_repo.get_by_name(organization_id, data["name"])
            if existing and existing["id"] != tax_id:
                raise ConflictError(f"Tax rate '{data['name']}' already exists")
        
        # Handle default flag
        if data.get("is_default"):
            await self.tax_repo.set_default(organization_id, tax_id)
        
        updated = await self.tax_repo.update(tax_id, data)
        return updated
    
    async def delete(
        self,
        tax_id: str,
        organization_id: str
    ) -> bool:
        """Delete tax rate (soft delete)"""
        await self.get(tax_id, organization_id)
        await self.tax_repo.update(tax_id, {"is_active": False})
        return True
    
    async def list(
        self,
        organization_id: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List all tax rates"""
        if include_inactive:
            return await self.tax_repo.get_all(
                organization_id,
                order_by="name",
                ascending=True
            )
        return await self.tax_repo.get_active(organization_id)
    
    async def get_default(
        self,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get default tax rate"""
        return await self.tax_repo.get_default(organization_id)
    
    async def set_default(
        self,
        tax_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Set a tax rate as default"""
        await self.get(tax_id, organization_id)
        return await self.tax_repo.set_default(organization_id, tax_id)

