"""
Report schemas
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime


class DateRangeRequest(BaseModel):
    """Date range filter"""
    start_date: date
    end_date: date


class RevenueReportItem(BaseModel):
    """Revenue report data point"""
    date: date
    revenue: float
    invoice_count: int


class RevenueReport(BaseModel):
    """Revenue report response"""
    start_date: date
    end_date: date
    total_revenue: float
    total_invoices: int
    paid_amount: float
    outstanding_amount: float
    data: List[RevenueReportItem]


class OutstandingInvoice(BaseModel):
    """Outstanding invoice item"""
    id: str
    invoice_number: str
    client_name: str
    issue_date: date
    due_date: date
    total: float
    balance_due: float
    days_overdue: int
    currency: str


class OutstandingReport(BaseModel):
    """Outstanding invoices report"""
    total_outstanding: float
    overdue_amount: float
    invoice_count: int
    overdue_count: int
    invoices: List[OutstandingInvoice]


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_invoices: int
    total_revenue: float
    paid_amount: float
    outstanding_amount: float
    overdue_amount: float
    overdue_count: int
    draft_count: int
    sent_count: int
    paid_count: int
    client_count: int
    currency: str


class RecentActivity(BaseModel):
    """Recent activity item"""
    id: str
    type: str  # invoice_created, invoice_sent, invoice_paid, client_added
    description: str
    timestamp: datetime
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None

