"""
Product service
"""
from typing import Optional, List, Dict, Any
from supabase import Client

from app.repositories.product import ProductRepository
from app.core.exceptions import NotFoundError, ConflictError


class ProductService:
    """Service for product/service operations"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.product_repo = ProductRepository(supabase)
    
    async def create(
        self,
        organization_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new product/service
        
        Args:
            organization_id: Organization UUID
            user_id: Creating user ID
            data: Product data
            
        Returns:
            Created product
        """
        # Check for duplicate SKU if provided
        if data.get("sku"):
            existing = await self.product_repo.get_by_sku(
                organization_id,
                data["sku"]
            )
            if existing:
                raise ConflictError(f"Product with SKU {data['sku']} already exists")
        
        # Add organization and audit fields
        data["organization_id"] = organization_id
        data["created_by"] = user_id
        
        return await self.product_repo.create(data)
    
    async def get(
        self,
        product_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get product by ID"""
        product = await self.product_repo.get_by_id(product_id)
        
        if not product or product.get("organization_id") != organization_id:
            raise NotFoundError("Product", product_id)
        
        return product
    
    async def update(
        self,
        product_id: str,
        organization_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update product"""
        # Verify product belongs to organization
        product = await self.get(product_id, organization_id)
        
        # Check for duplicate SKU if being changed
        if data.get("sku") and data["sku"] != product.get("sku"):
            existing = await self.product_repo.get_by_sku(
                organization_id,
                data["sku"]
            )
            if existing and existing["id"] != product_id:
                raise ConflictError(f"Product with SKU {data['sku']} already exists")
        
        updated = await self.product_repo.update(product_id, data)
        if not updated:
            raise NotFoundError("Product", product_id)
        
        return updated
    
    async def delete(
        self,
        product_id: str,
        organization_id: str
    ) -> bool:
        """Delete product (soft delete by deactivating)"""
        # Verify product belongs to organization
        await self.get(product_id, organization_id)
        
        await self.product_repo.update(product_id, {"is_active": False})
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
        List products with pagination
        
        Args:
            organization_id: Organization UUID
            search: Optional search query
            include_inactive: Include inactive products
            page: Page number
            per_page: Items per page
            
        Returns:
            Dict with products and pagination info
        """
        offset = (page - 1) * per_page
        
        if search:
            products = await self.product_repo.search(
                organization_id,
                search,
                limit=per_page
            )
            total = len(products)
        else:
            filters = None if include_inactive else {"is_active": True}
            products = await self.product_repo.get_all(
                organization_id,
                filters=filters,
                order_by="name",
                ascending=True,
                limit=per_page,
                offset=offset
            )
            total = await self.product_repo.count(organization_id, filters)
        
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "products": products,
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
        """Search products by name or SKU"""
        return await self.product_repo.search(organization_id, query, limit)

