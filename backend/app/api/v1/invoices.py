"""
Invoice API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.invoice import InvoiceService
from app.services.pdf import PDFService
from app.services.email import EmailService
from app.services.organization import OrganizationService
from app.repositories.invoice import InvoiceRepository
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceItemCreate,
    InvoiceItemUpdate,
    MarkPaidRequest,
    SendInvoiceRequest
)
from app.schemas.common import SuccessResponse, DeleteResponse, MessageResponse

router = APIRouter()


@router.get("", response_model=SuccessResponse)
async def list_invoices(
    status: Optional[str] = Query(None, description="Filter by status"),
    client_id: Optional[str] = Query(None, description="Filter by client"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    List all invoices for the organization
    
    Supports filtering by status and client.
    """
    invoice_service = InvoiceService(supabase)
    
    # Handle string "None" or "null" from query params
    if client_id in ("None", "null", "undefined", ""):
        client_id = None
    if status in ("None", "null", "undefined", ""):
        status = None
    
    # Get organization_id and handle invalid values
    organization_id = current_user.get("organization_id")
    if not organization_id:
        # User not associated with an organization, return empty list
        return SuccessResponse(data={
            "invoices": [],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0
            }
        })
    
    result = await invoice_service.list(
        organization_id=organization_id,
        status=status,
        client_id=client_id,
        page=page,
        per_page=per_page
    )
    
    return SuccessResponse(data=result)


@router.post("", response_model=SuccessResponse[InvoiceResponse], status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new invoice
    
    Include line items in the request body.
    """
    invoice_service = InvoiceService(supabase)
    
    invoice = await invoice_service.create(
        organization_id=current_user["organization_id"],
        user_id=current_user["id"],
        data=data.model_dump()
    )
    
    return SuccessResponse(data=invoice, message="Invoice created successfully")


@router.get("/{invoice_id}", response_model=SuccessResponse[InvoiceResponse])
async def get_invoice(
    invoice_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get invoice by ID with line items"""
    invoice_service = InvoiceService(supabase)
    
    invoice = await invoice_service.get(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    
    return SuccessResponse(data=invoice)


@router.patch("/{invoice_id}", response_model=SuccessResponse[InvoiceResponse])
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Update invoice
    
    Only draft invoices can be edited.
    """
    invoice_service = InvoiceService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    invoice = await invoice_service.update(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"],
        data=update_data
    )
    
    return SuccessResponse(data=invoice, message="Invoice updated successfully")


@router.delete("/{invoice_id}", response_model=DeleteResponse)
async def delete_invoice(
    invoice_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete invoice
    
    Only draft invoices can be deleted.
    """
    invoice_service = InvoiceService(supabase)
    
    await invoice_service.delete(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    
    return DeleteResponse(message="Invoice deleted successfully")


# Invoice items endpoints

@router.post("/{invoice_id}/items", response_model=SuccessResponse, status_code=201)
async def add_invoice_item(
    invoice_id: str,
    data: InvoiceItemCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Add a line item to an invoice"""
    invoice_service = InvoiceService(supabase)
    
    item = await invoice_service.add_item(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"],
        item_data=data.model_dump()
    )
    
    return SuccessResponse(data=item, message="Item added successfully")


@router.patch("/{invoice_id}/items/{item_id}", response_model=SuccessResponse)
async def update_invoice_item(
    invoice_id: str,
    item_id: str,
    data: InvoiceItemUpdate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Update a line item"""
    invoice_service = InvoiceService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    item = await invoice_service.update_item(
        invoice_id=invoice_id,
        item_id=item_id,
        organization_id=current_user["organization_id"],
        item_data=update_data
    )
    
    return SuccessResponse(data=item, message="Item updated successfully")


@router.delete("/{invoice_id}/items/{item_id}", response_model=DeleteResponse)
async def delete_invoice_item(
    invoice_id: str,
    item_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Delete a line item"""
    invoice_service = InvoiceService(supabase)
    
    await invoice_service.delete_item(
        invoice_id=invoice_id,
        item_id=item_id,
        organization_id=current_user["organization_id"]
    )
    
    return DeleteResponse(message="Item deleted successfully")


# Invoice actions

@router.post("/{invoice_id}/send", response_model=SuccessResponse)
async def send_invoice(
    invoice_id: str,
    data: SendInvoiceRequest,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Send invoice via email
    
    Generates PDF and sends to client email.
    """
    invoice_service = InvoiceService(supabase)
    pdf_service = PDFService(supabase)
    email_service = EmailService(supabase)
    org_service = OrganizationService(supabase)
    
    # Get invoice and organization
    invoice = await invoice_service.get(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    org = await org_service.get(current_user["organization_id"])
    
    # Determine recipient email
    recipient_email = data.recipient_email
    if not recipient_email and invoice.get("client"):
        recipient_email = invoice["client"].get("email")
    
    if not recipient_email:
        raise ValueError("No recipient email provided and client has no email")
    
    # Generate PDF
    pdf_bytes = None
    if data.attach_pdf:
        pdf_bytes = await pdf_service.generate_invoice_pdf(invoice, org)
        
        # Save PDF to storage
        pdf_url = await pdf_service.save_to_storage(
            pdf_bytes,
            invoice_id,
            current_user["organization_id"]
        )
        
        # Update invoice with PDF URL
        invoice_repo = InvoiceRepository(supabase)
        await invoice_repo.update_pdf_url(invoice_id, pdf_url)
    
    # Send email
    email_log = await email_service.send_invoice_email(
        organization_id=current_user["organization_id"],
        invoice=invoice,
        recipient_email=recipient_email,
        subject=data.subject,
        message=data.message,
        pdf_bytes=pdf_bytes,
        sender_name=org.get("name")
    )
    
    # Mark invoice as sent
    await invoice_service.mark_as_sent(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    
    return SuccessResponse(
        data={"email_log": email_log},
        message="Invoice sent successfully"
    )


@router.post("/{invoice_id}/mark-paid", response_model=SuccessResponse[InvoiceResponse])
async def mark_invoice_paid(
    invoice_id: str,
    data: MarkPaidRequest,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Mark invoice as paid"""
    invoice_service = InvoiceService(supabase)
    
    invoice = await invoice_service.mark_as_paid(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"],
        amount_paid=data.amount_paid,
        paid_at=data.paid_at
    )
    
    return SuccessResponse(data=invoice, message="Invoice marked as paid")


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Download invoice as PDF"""
    invoice_service = InvoiceService(supabase)
    pdf_service = PDFService(supabase)
    org_service = OrganizationService(supabase)
    
    # Get invoice and organization
    invoice = await invoice_service.get(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    org = await org_service.get(current_user["organization_id"])
    
    # Generate PDF
    pdf_bytes = await pdf_service.generate_invoice_pdf(invoice, org)
    
    # Return PDF response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice-{invoice['invoice_number']}.pdf"
        }
    )


@router.get("/{invoice_id}/emails")
async def get_invoice_emails(
    invoice_id: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get all emails sent for an invoice"""
    # Verify invoice belongs to organization
    invoice_service = InvoiceService(supabase)
    await invoice_service.get(
        invoice_id=invoice_id,
        organization_id=current_user["organization_id"]
    )
    
    email_service = EmailService(supabase)
    emails = await email_service.get_invoice_emails(invoice_id)
    
    return SuccessResponse(data=emails)

