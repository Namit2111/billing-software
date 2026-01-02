"""
Dashboard service
"""
from typing import Dict, Any, List
from datetime import date, datetime, timedelta
from supabase import Client

from app.repositories.invoice import InvoiceRepository
from app.repositories.client import ClientRepository


class DashboardService:
    """Service for dashboard and reporting"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.invoice_repo = InvoiceRepository(supabase)
        self.client_repo = ClientRepository(supabase)
    
    async def get_stats(
        self,
        organization_id: str,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get dashboard statistics"""
        # Get invoice totals
        totals = await self.invoice_repo.get_totals(organization_id)
        
        # Get client count
        client_count = await self.client_repo.count(
            organization_id,
            {"is_active": True}
        )
        
        return {
            "total_invoices": totals["invoice_count"],
            "total_revenue": totals["total_revenue"],
            "paid_amount": totals["paid_amount"],
            "outstanding_amount": totals["outstanding_amount"],
            "overdue_amount": totals["overdue_amount"],
            "overdue_count": totals["overdue_count"],
            "draft_count": totals["draft_count"],
            "sent_count": totals["sent_count"],
            "paid_count": totals["paid_count"],
            "client_count": client_count,
            "currency": currency
        }
    
    async def get_revenue_report(
        self,
        organization_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get revenue report for date range"""
        invoices = await self.invoice_repo.get_by_date_range(
            organization_id,
            start_date,
            end_date
        )
        
        # Group by date
        daily_data = {}
        total_revenue = 0
        paid_amount = 0
        outstanding_amount = 0
        
        for inv in invoices:
            inv_date = inv.get("issue_date", "")
            if isinstance(inv_date, str):
                inv_date = date.fromisoformat(inv_date)
            
            date_key = inv_date.isoformat()
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": inv_date,
                    "revenue": 0,
                    "invoice_count": 0
                }
            
            daily_data[date_key]["revenue"] += inv.get("total", 0)
            daily_data[date_key]["invoice_count"] += 1
            
            total_revenue += inv.get("total", 0)
            
            if inv.get("status") == "paid":
                paid_amount += inv.get("amount_paid", 0)
            else:
                outstanding_amount += inv.get("total", 0) - inv.get("amount_paid", 0)
        
        # Sort by date
        data = sorted(daily_data.values(), key=lambda x: x["date"])
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": total_revenue,
            "total_invoices": len(invoices),
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding_amount,
            "data": data
        }
    
    async def get_outstanding_report(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get outstanding invoices report"""
        invoices = await self.invoice_repo.get_outstanding(organization_id)
        
        today = date.today()
        total_outstanding = 0
        overdue_amount = 0
        overdue_count = 0
        
        result_invoices = []
        
        for inv in invoices:
            due_date = inv.get("due_date", "")
            if isinstance(due_date, str):
                due_date = date.fromisoformat(due_date)
            
            balance = inv.get("total", 0) - inv.get("amount_paid", 0)
            days_overdue = (today - due_date).days if today > due_date else 0
            
            total_outstanding += balance
            
            if days_overdue > 0:
                overdue_amount += balance
                overdue_count += 1
            
            # Get client name
            client_name = ""
            if inv.get("clients"):
                client_name = inv["clients"].get("name", "")
            
            result_invoices.append({
                "id": inv["id"],
                "invoice_number": inv["invoice_number"],
                "client_name": client_name,
                "issue_date": inv["issue_date"],
                "due_date": inv["due_date"],
                "total": inv["total"],
                "balance_due": balance,
                "days_overdue": days_overdue,
                "currency": inv.get("currency", "USD")
            })
        
        # Sort by days overdue (most overdue first)
        result_invoices.sort(key=lambda x: x["days_overdue"], reverse=True)
        
        return {
            "total_outstanding": total_outstanding,
            "overdue_amount": overdue_amount,
            "invoice_count": len(invoices),
            "overdue_count": overdue_count,
            "invoices": result_invoices
        }
    
    async def get_recent_activity(
        self,
        organization_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activity"""
        # Get recent invoices
        invoices = await self.invoice_repo.get_recent(organization_id, limit)
        
        activities = []
        
        for inv in invoices:
            # Determine activity type based on status
            status = inv.get("status", "draft")
            
            if status == "paid" and inv.get("paid_at"):
                activities.append({
                    "id": f"{inv['id']}-paid",
                    "type": "invoice_paid",
                    "description": f"Invoice {inv['invoice_number']} was marked as paid",
                    "timestamp": inv["paid_at"],
                    "invoice_id": inv["id"]
                })
            
            if inv.get("sent_at"):
                activities.append({
                    "id": f"{inv['id']}-sent",
                    "type": "invoice_sent",
                    "description": f"Invoice {inv['invoice_number']} was sent",
                    "timestamp": inv["sent_at"],
                    "invoice_id": inv["id"]
                })
            
            activities.append({
                "id": f"{inv['id']}-created",
                "type": "invoice_created",
                "description": f"Invoice {inv['invoice_number']} was created",
                "timestamp": inv["created_at"],
                "invoice_id": inv["id"]
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
    
    async def export_invoices_csv(
        self,
        organization_id: str,
        start_date: date,
        end_date: date
    ) -> str:
        """Export invoices to CSV format"""
        invoices = await self.invoice_repo.get_by_date_range(
            organization_id,
            start_date,
            end_date
        )
        
        # Build CSV
        headers = [
            "Invoice Number", "Client", "Status", "Issue Date", "Due Date",
            "Subtotal", "Tax", "Total", "Amount Paid", "Balance Due", "Currency"
        ]
        
        lines = [",".join(headers)]
        
        for inv in invoices:
            client = await self.client_repo.get_by_id(inv.get("client_id", ""))
            client_name = client.get("name", "") if client else ""
            
            row = [
                inv.get("invoice_number", ""),
                f'"{client_name}"',
                inv.get("status", ""),
                str(inv.get("issue_date", "")),
                str(inv.get("due_date", "")),
                str(inv.get("subtotal", 0)),
                str(inv.get("tax_total", 0)),
                str(inv.get("total", 0)),
                str(inv.get("amount_paid", 0)),
                str(inv.get("total", 0) - inv.get("amount_paid", 0)),
                inv.get("currency", "USD")
            ]
            lines.append(",".join(row))
        
        return "\n".join(lines)

