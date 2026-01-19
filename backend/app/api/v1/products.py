"""
Product API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.product import ProductService
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from app.schemas.common import SuccessResponse, DeleteResponse

router = APIRouter()


@router.get("", response_model=SuccessResponse)
async def list_products(
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    include_inactive: bool = Query(False),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    List all products/services for the organization
    
    Supports search and pagination.
    """
    product_service = ProductService(supabase)
    
    # Handle string "None" or "null" from query params
    if search in ("None", "null", "undefined", ""):
        search = None
    
    # Check if user has an organization
    organization_id = current_user.get("organization_id")
    if not organization_id:
        return SuccessResponse(data={
            "products": [],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0
            }
        })
    
    result = await product_service.list(
        organization_id=organization_id,
        search=search,
        include_inactive=include_inactive,
        page=page,
        per_page=per_page
    )
    
    return SuccessResponse(data=result)


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Quick search for products (for autocomplete)"""
    product_service = ProductService(supabase)
    
    products = await product_service.search(
        organization_id=current_user["organization_id"],
        query=q,
        limit=limit
    )
    
    return SuccessResponse(data=products)


@router.post("", response_model=SuccessResponse[ProductResponse], status_code=201)
async def create_product(
    data: ProductCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Create a new product/service"""
    product_service = ProductService(supabase)
    
    product = await product_service.create(
        organization_id=current_user["organization_id"],
        user_id=current_user["id"],
        data=data.model_dump()
    )
    
    return SuccessResponse(data=product, message="Product created successfully")


@router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def get_product(
    product_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get product by ID"""
    product_service = ProductService(supabase)
    
    product = await product_service.get(
        product_id=product_id,
        organization_id=current_user["organization_id"]
    )
    
    return SuccessResponse(data=product)


@router.patch("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def update_product(
    product_id: str,
    data: ProductUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Update product"""
    product_service = ProductService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    product = await product_service.update(
        product_id=product_id,
        organization_id=current_user["organization_id"],
        data=update_data
    )
    
    return SuccessResponse(data=product, message="Product updated successfully")


@router.delete("/{product_id}", response_model=DeleteResponse)
async def delete_product(
    product_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Delete product (soft delete)"""
    product_service = ProductService(supabase)
    
    await product_service.delete(
        product_id=product_id,
        organization_id=current_user["organization_id"]
    )
    
    return DeleteResponse(message="Product deleted successfully")

