"""
Client API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.client import ClientService
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse
)
from app.schemas.common import SuccessResponse, PaginatedResponse, DeleteResponse

router = APIRouter()


@router.get("", response_model=SuccessResponse)
async def list_clients(
    search: Optional[str] = Query(None, description="Search by name, email, or company"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    include_inactive: bool = Query(False),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    List all clients for the organization
    
    Supports search and pagination.
    """
    client_service = ClientService(supabase)
    
    result = await client_service.list(
        organization_id=current_user["organization_id"],
        search=search,
        include_inactive=include_inactive,
        page=page,
        per_page=per_page
    )
    
    return SuccessResponse(data=result)


@router.get("/search")
async def search_clients(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Quick search for clients (for autocomplete)"""
    client_service = ClientService(supabase)
    
    clients = await client_service.search(
        organization_id=current_user["organization_id"],
        query=q,
        limit=limit
    )
    
    return SuccessResponse(data=clients)


@router.post("", response_model=SuccessResponse[ClientResponse], status_code=201)
async def create_client(
    data: ClientCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Create a new client"""
    client_service = ClientService(supabase)
    
    client = await client_service.create(
        organization_id=current_user["organization_id"],
        user_id=current_user["id"],
        data=data.model_dump()
    )
    
    return SuccessResponse(data=client, message="Client created successfully")


@router.get("/{client_id}", response_model=SuccessResponse[ClientResponse])
async def get_client(
    client_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get client by ID"""
    client_service = ClientService(supabase)
    
    client = await client_service.get(
        client_id=client_id,
        organization_id=current_user["organization_id"]
    )
    
    return SuccessResponse(data=client)


@router.patch("/{client_id}", response_model=SuccessResponse[ClientResponse])
async def update_client(
    client_id: str,
    data: ClientUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Update client"""
    client_service = ClientService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    client = await client_service.update(
        client_id=client_id,
        organization_id=current_user["organization_id"],
        data=update_data
    )
    
    return SuccessResponse(data=client, message="Client updated successfully")


@router.delete("/{client_id}", response_model=DeleteResponse)
async def delete_client(
    client_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Delete client (soft delete)"""
    client_service = ClientService(supabase)
    
    await client_service.delete(
        client_id=client_id,
        organization_id=current_user["organization_id"]
    )
    
    return DeleteResponse(message="Client deleted successfully")

