"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.dashboard import DashboardService
from app.services.organization import OrganizationService
from app.schemas.reports import DashboardStats, RecentActivity
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.get("/stats", response_model=SuccessResponse[DashboardStats])
async def get_dashboard_stats(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get dashboard statistics

    Returns overview of invoices, revenue, and outstanding amounts.
    """
    # Check if user has an organization
    organization_id = current_user.get("organization_id")
    if not organization_id:
        return SuccessResponse(data={
            "total_invoices": 0,
            "total_revenue": 0,
            "paid_amount": 0,
            "outstanding_amount": 0,
            "overdue_amount": 0,
            "overdue_count": 0,
            "draft_count": 0,
            "sent_count": 0,
            "paid_count": 0,
            "client_count": 0,
            "currency": "USD"
        })

    dashboard_service = DashboardService(supabase)
    org_service = OrganizationService(supabase)

    # Get organization currency
    org = await org_service.get(organization_id)

    stats = await dashboard_service.get_stats(
        organization_id=organization_id,
        currency=org.get("currency", "USD")
    )

    return SuccessResponse(data=stats)


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recent activity

    Returns list of recent invoice and client activities.
    """
    # Check if user has an organization
    organization_id = current_user.get("organization_id")
    if not organization_id:
        return SuccessResponse(data=[])

    dashboard_service = DashboardService(supabase)

    activities = await dashboard_service.get_recent_activity(
        organization_id=organization_id,
        limit=limit
    )

    return SuccessResponse(data=activities)


@router.get("/overdue")
async def get_overdue_invoices(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get overdue invoices

    Returns list of invoices past their due date.
    """
    # Check if user has an organization
    organization_id = current_user.get("organization_id")
    if not organization_id:
        return SuccessResponse(data=[])

    from app.services.invoice import InvoiceService

    invoice_service = InvoiceService(supabase)

    overdue = await invoice_service.get_overdue(
        organization_id=organization_id
    )

    return SuccessResponse(data=overdue)

