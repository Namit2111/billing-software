"""
Settings API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from supabase import Client

from app.core.dependencies import (
    get_supabase_admin_client,
    get_current_user,
    require_owner
)
from app.services.organization import OrganizationService
from app.services.tax import TaxService
from app.schemas.organization import (
    OrganizationUpdate,
    OrganizationResponse,
    InvoiceSettingsUpdate
)
from app.schemas.tax import TaxCreate, TaxUpdate, TaxResponse
from app.schemas.common import SuccessResponse, DeleteResponse, MessageResponse

router = APIRouter()


# Organization settings

@router.get("/organization", response_model=SuccessResponse[OrganizationResponse])
async def get_organization_settings(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get organization settings"""
    org_service = OrganizationService(supabase)
    org = await org_service.get(current_user["organization_id"])
    
    return SuccessResponse(data=org)


@router.patch("/organization", response_model=SuccessResponse[OrganizationResponse])
async def update_organization_settings(
    data: OrganizationUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """
    Update organization settings
    
    Requires owner role.
    """
    org_service = OrganizationService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    org = await org_service.update(
        organization_id=current_user["organization_id"],
        user_id=current_user["id"],
        data=update_data
    )
    
    return SuccessResponse(data=org, message="Settings updated successfully")


@router.post("/organization/logo", response_model=SuccessResponse)
async def upload_organization_logo(
    file: UploadFile = File(...),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """
    Upload organization logo
    
    Requires owner role. Accepts PNG, JPG, or SVG.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Read file
    content = await file.read()
    
    # Upload
    org_service = OrganizationService(supabase)
    url = await org_service.upload_logo(
        organization_id=current_user["organization_id"],
        file_content=content,
        filename=file.filename
    )
    
    return SuccessResponse(
        data={"logo_url": url},
        message="Logo uploaded successfully"
    )


# Invoice settings

@router.patch("/invoice", response_model=SuccessResponse[OrganizationResponse])
async def update_invoice_settings(
    data: InvoiceSettingsUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """
    Update invoice-related settings
    
    Includes prefix, default tax rate, and payment terms.
    """
    org_service = OrganizationService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    org = await org_service.update(
        organization_id=current_user["organization_id"],
        user_id=current_user["id"],
        data=update_data
    )
    
    return SuccessResponse(data=org, message="Invoice settings updated")


# Tax settings

@router.get("/taxes", response_model=SuccessResponse[List[TaxResponse]])
async def list_taxes(
    include_inactive: bool = False,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """List all tax rates"""
    tax_service = TaxService(supabase)
    
    taxes = await tax_service.list(
        organization_id=current_user["organization_id"],
        include_inactive=include_inactive
    )
    
    return SuccessResponse(data=taxes)


@router.post("/taxes", response_model=SuccessResponse[TaxResponse], status_code=201)
async def create_tax(
    data: TaxCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """Create a new tax rate"""
    tax_service = TaxService(supabase)
    
    tax = await tax_service.create(
        organization_id=current_user["organization_id"],
        data=data.model_dump()
    )
    
    return SuccessResponse(data=tax, message="Tax rate created successfully")


@router.patch("/taxes/{tax_id}", response_model=SuccessResponse[TaxResponse])
async def update_tax(
    tax_id: str,
    data: TaxUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """Update a tax rate"""
    tax_service = TaxService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    tax = await tax_service.update(
        tax_id=tax_id,
        organization_id=current_user["organization_id"],
        data=update_data
    )
    
    return SuccessResponse(data=tax, message="Tax rate updated successfully")


@router.delete("/taxes/{tax_id}", response_model=DeleteResponse)
async def delete_tax(
    tax_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(require_owner)
):
    """Delete a tax rate"""
    tax_service = TaxService(supabase)
    
    await tax_service.delete(
        tax_id=tax_id,
        organization_id=current_user["organization_id"]
    )
    
    return DeleteResponse(message="Tax rate deleted successfully")


# Team members

@router.get("/members")
async def list_members(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """List organization members"""
    org_service = OrganizationService(supabase)
    
    members = await org_service.get_members(current_user["organization_id"])
    
    return SuccessResponse(data=members)

