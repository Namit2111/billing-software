"""
Reports API endpoints
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, Response
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.dashboard import DashboardService
from app.schemas.reports import DateRangeRequest, RevenueReport, OutstandingReport
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.get("/revenue", response_model=SuccessResponse[RevenueReport])
async def get_revenue_report(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get revenue report for date range
    
    Returns daily revenue breakdown with totals.
    """
    dashboard_service = DashboardService(supabase)
    
    report = await dashboard_service.get_revenue_report(
        organization_id=current_user["organization_id"],
        start_date=start_date,
        end_date=end_date
    )
    
    return SuccessResponse(data=report)


@router.get("/outstanding", response_model=SuccessResponse[OutstandingReport])
async def get_outstanding_report(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get outstanding invoices report
    
    Returns all unpaid invoices with aging information.
    """
    dashboard_service = DashboardService(supabase)
    
    report = await dashboard_service.get_outstanding_report(
        organization_id=current_user["organization_id"]
    )
    
    return SuccessResponse(data=report)


@router.get("/export/invoices")
async def export_invoices_csv(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Export invoices to CSV
    
    Downloads a CSV file of invoices for the date range.
    """
    dashboard_service = DashboardService(supabase)
    
    csv_content = await dashboard_service.export_invoices_csv(
        organization_id=current_user["organization_id"],
        start_date=start_date,
        end_date=end_date
    )
    
    filename = f"invoices-{start_date}-to-{end_date}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/summary")
async def get_monthly_summary(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """
    Get monthly summary report
    
    Returns invoice statistics for a specific month.
    """
    dashboard_service = DashboardService(supabase)
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    report = await dashboard_service.get_revenue_report(
        organization_id=current_user["organization_id"],
        start_date=start_date,
        end_date=end_date
    )
    
    return SuccessResponse(data={
        "year": year,
        "month": month,
        **report
    })

