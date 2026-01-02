"""
Base repository with common CRUD operations
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from datetime import datetime
from supabase import Client
import uuid


T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository class with common CRUD operations
    All repositories should inherit from this class
    """
    
    def __init__(self, supabase: Client, table_name: str):
        """
        Initialize repository
        
        Args:
            supabase: Supabase client instance
            table_name: Name of the database table
        """
        self.supabase = supabase
        self.table_name = table_name
    
    def _generate_id(self) -> str:
        """Generate a new UUID"""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp as ISO string"""
        return datetime.utcnow().isoformat()
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID
        
        Args:
            id: Record UUID
            
        Returns:
            Record data or None
        """
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", id).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def get_all(
        self,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        ascending: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all records for an organization with optional filters
        
        Args:
            organization_id: Organization UUID
            filters: Optional additional filters
            order_by: Field to order by
            ascending: Sort order
            limit: Max records to return
            offset: Number of records to skip
            
        Returns:
            List of records
        """
        query = self.supabase.table(self.table_name).select("*").eq("organization_id", organization_id)
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)
        
        # Apply ordering
        query = query.order(order_by, desc=not ascending)
        
        # Apply pagination
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        response = query.execute()
        return response.data or []
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record
        
        Args:
            data: Record data
            
        Returns:
            Created record
        """
        # Ensure ID and timestamps
        if "id" not in data:
            data["id"] = self._generate_id()
        if "created_at" not in data:
            data["created_at"] = self._get_timestamp()
        if "updated_at" not in data:
            data["updated_at"] = self._get_timestamp()
        
        response = self.supabase.table(self.table_name).insert(data).execute()
        return response.data[0] if response.data else None
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a record by ID
        
        Args:
            id: Record UUID
            data: Fields to update
            
        Returns:
            Updated record or None
        """
        # Update timestamp
        data["updated_at"] = self._get_timestamp()
        
        response = self.supabase.table(self.table_name).update(data).eq("id", id).execute()
        return response.data[0] if response.data else None
    
    async def delete(self, id: str) -> bool:
        """
        Delete a record by ID (hard delete)
        
        Args:
            id: Record UUID
            
        Returns:
            True if deleted successfully
        """
        response = self.supabase.table(self.table_name).delete().eq("id", id).execute()
        return True
    
    async def soft_delete(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Soft delete a record by setting deleted_at
        
        Args:
            id: Record UUID
            
        Returns:
            Updated record or None
        """
        return await self.update(id, {"deleted_at": self._get_timestamp()})
    
    async def count(
        self,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records for an organization
        
        Args:
            organization_id: Organization UUID
            filters: Optional filters
            
        Returns:
            Record count
        """
        query = self.supabase.table(self.table_name).select("id", count="exact").eq("organization_id", organization_id)
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)
        
        response = query.execute()
        return response.count or 0
    
    async def exists(self, id: str, organization_id: str) -> bool:
        """
        Check if a record exists
        
        Args:
            id: Record UUID
            organization_id: Organization UUID
            
        Returns:
            True if exists
        """
        response = self.supabase.table(self.table_name).select("id").eq("id", id).eq("organization_id", organization_id).execute()
        return len(response.data or []) > 0

