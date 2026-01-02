"""
Client service
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.client import ClientRepository
from app.core.exceptions import NotFoundError, ConflictError


class ClientService:
    """Service for client operations"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.client_repo = ClientRepository(supabase)
    
    async def create(
        self,
        organization_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new client
        
        Args:
            organization_id: Organization UUID
            user_id: Creating user ID
            data: Client data
            
        Returns:
            Created client
        """
        # Check for duplicate email if provided
        if data.get("email"):
            existing = await self.client_repo.get_by_email(
                organization_id,
                data["email"]
            )
            if existing:
                raise ConflictError(f"Client with email {data['email']} already exists")
        
        # Add organization and audit fields
        data["organization_id"] = organization_id
        data["created_by"] = user_id
        
        return await self.client_repo.create(data)
    
    async def get(
        self,
        client_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get client by ID"""
        client = await self.client_repo.get_by_id(client_id)
        
        if not client or client.get("organization_id") != organization_id:
            raise NotFoundError("Client", client_id)
        
        return client
    
    async def update(
        self,
        client_id: str,
        organization_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client"""
        # Verify client belongs to organization
        client = await self.get(client_id, organization_id)
        
        # Check for duplicate email if being changed
        if data.get("email") and data["email"] != client.get("email"):
            existing = await self.client_repo.get_by_email(
                organization_id,
                data["email"]
            )
            if existing and existing["id"] != client_id:
                raise ConflictError(f"Client with email {data['email']} already exists")
        
        updated = await self.client_repo.update(client_id, data)
        if not updated:
            raise NotFoundError("Client", client_id)
        
        return updated
    
    async def delete(
        self,
        client_id: str,
        organization_id: str
    ) -> bool:
        """Delete client (soft delete by deactivating)"""
        # Verify client belongs to organization
        await self.get(client_id, organization_id)
        
        await self.client_repo.update(client_id, {"is_active": False})
        return True
    
    async def list(
        self,
        organization_id: str,
        search: Optional[str] = None,
        include_inactive: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        List clients with pagination
        
        Args:
            organization_id: Organization UUID
            search: Optional search query
            include_inactive: Include inactive clients
            page: Page number
            per_page: Items per page
            
        Returns:
            Dict with clients and pagination info
        """
        offset = (page - 1) * per_page
        
        if search:
            clients = await self.client_repo.search(
                organization_id,
                search,
                limit=per_page
            )
            total = len(clients)
        else:
            filters = None if include_inactive else {"is_active": True}
            clients = await self.client_repo.get_all(
                organization_id,
                filters=filters,
                order_by="name",
                ascending=True,
                limit=per_page,
                offset=offset
            )
            total = await self.client_repo.count(organization_id, filters)
        
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "clients": clients,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    async def search(
        self,
        organization_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search clients by name, email, or company"""
        return await self.client_repo.search(organization_id, query, limit)

