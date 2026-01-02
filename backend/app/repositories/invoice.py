"""
Invoice repository
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from supabase import Client

from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository):
    """Repository for invoice operations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "invoices")
    
    async def get_by_id_with_items(self, id: str) -> Optional[Dict[str, Any]]:
        """Get invoice with line items and client data"""
        # Get invoice
        try:
            response = self.supabase.table(self.table_name)\
                .select("*, clients(*)")\
                .eq("id", id)\
                .limit(1)\
                .execute()
            
            if not response.data:
                return None
            
            invoice = response.data[0]
        except Exception:
            return None
        
        # Get line items
        items_response = self.supabase.table("invoice_items")\
            .select("*")\
            .eq("invoice_id", id)\
            .order("sort_order")\
            .execute()
        
        invoice["items"] = items_response.data or []
        invoice["client"] = invoice.pop("clients", None)
        
        return invoice
    
    async def get_by_number(
        self,
        organization_id: str,
        invoice_number: str
    ) -> Optional[Dict[str, Any]]:
        """Get invoice by invoice number"""
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("organization_id", organization_id)\
                .eq("invoice_number", invoice_number)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def get_by_status(
        self,
        organization_id: str,
        status: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get invoices by status"""
        return await self.get_all(
            organization_id=organization_id,
            filters={"status": status},
            limit=limit,
            offset=offset
        )
    
    async def get_by_client(
        self,
        client_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all invoices for a client"""
        query = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("client_id", client_id)\
            .order("created_at", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data or []
    
    async def get_overdue(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get all overdue invoices"""
        today = date.today().isoformat()
        
        response = self.supabase.table(self.table_name)\
            .select("*, clients(name)")\
            .eq("organization_id", organization_id)\
            .in_("status", ["sent", "overdue"])\
            .lt("due_date", today)\
            .order("due_date")\
            .execute()
        
        return response.data or []
    
    async def get_outstanding(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get all outstanding (unpaid) invoices"""
        response = self.supabase.table(self.table_name)\
            .select("*, clients(name)")\
            .eq("organization_id", organization_id)\
            .in_("status", ["sent", "overdue"])\
            .order("due_date")\
            .execute()
        
        return response.data or []
    
    async def get_by_date_range(
        self,
        organization_id: str,
        start_date: date,
        end_date: date,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get invoices within date range"""
        query = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("organization_id", organization_id)\
            .gte("issue_date", start_date.isoformat())\
            .lte("issue_date", end_date.isoformat())
        
        if status:
            query = query.eq("status", status)
        
        response = query.order("issue_date").execute()
        return response.data or []
    
    async def update_status(
        self,
        id: str,
        status: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update invoice status"""
        data = {"status": status}
        if additional_data:
            data.update(additional_data)
        return await self.update(id, data)
    
    async def mark_as_sent(self, id: str) -> Optional[Dict[str, Any]]:
        """Mark invoice as sent"""
        return await self.update_status(id, "sent", {
            "sent_at": datetime.utcnow().isoformat()
        })
    
    async def mark_as_paid(
        self,
        id: str,
        amount_paid: float,
        paid_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark invoice as paid"""
        return await self.update_status(id, "paid", {
            "amount_paid": amount_paid,
            "paid_at": (paid_at or datetime.utcnow()).isoformat()
        })
    
    async def update_pdf_url(self, id: str, pdf_url: str) -> Optional[Dict[str, Any]]:
        """Update invoice PDF URL"""
        return await self.update(id, {"pdf_url": pdf_url})
    
    async def get_totals(
        self,
        organization_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, float]:
        """Get invoice totals for dashboard"""
        query = self.supabase.table(self.table_name)\
            .select("status, total, amount_paid")\
            .eq("organization_id", organization_id)
        
        if start_date:
            query = query.gte("issue_date", start_date.isoformat())
        if end_date:
            query = query.lte("issue_date", end_date.isoformat())
        
        response = query.execute()
        invoices = response.data or []
        
        totals = {
            "total_revenue": 0,
            "paid_amount": 0,
            "outstanding_amount": 0,
            "overdue_amount": 0,
            "invoice_count": len(invoices),
            "paid_count": 0,
            "sent_count": 0,
            "draft_count": 0,
            "overdue_count": 0
        }
        
        today = date.today()
        
        for inv in invoices:
            status = inv.get("status", "draft")
            total = inv.get("total", 0)
            paid = inv.get("amount_paid", 0)
            
            totals["total_revenue"] += total
            totals["paid_amount"] += paid
            
            if status == "paid":
                totals["paid_count"] += 1
            elif status == "sent":
                totals["sent_count"] += 1
                totals["outstanding_amount"] += (total - paid)
            elif status == "overdue":
                totals["overdue_count"] += 1
                totals["overdue_amount"] += (total - paid)
                totals["outstanding_amount"] += (total - paid)
            elif status == "draft":
                totals["draft_count"] += 1
        
        return totals
    
    async def get_recent(
        self,
        organization_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent invoices"""
        response = self.supabase.table(self.table_name)\
            .select("*, clients(name)")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data or []


class InvoiceItemRepository(BaseRepository):
    """Repository for invoice line items"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "invoice_items")
    
    async def get_by_invoice(self, invoice_id: str) -> List[Dict[str, Any]]:
        """Get all items for an invoice"""
        response = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("invoice_id", invoice_id)\
            .order("sort_order")\
            .execute()
        
        return response.data or []
    
    async def create_bulk(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple invoice items"""
        for item in items:
            if "id" not in item:
                item["id"] = self._generate_id()
            if "created_at" not in item:
                item["created_at"] = self._get_timestamp()
            if "updated_at" not in item:
                item["updated_at"] = self._get_timestamp()
        
        response = self.supabase.table(self.table_name).insert(items).execute()
        return response.data or []
    
    async def delete_by_invoice(self, invoice_id: str) -> bool:
        """Delete all items for an invoice"""
        self.supabase.table(self.table_name)\
            .delete()\
            .eq("invoice_id", invoice_id)\
            .execute()
        return True
    
    async def update_sort_order(
        self,
        item_id: str,
        sort_order: int
    ) -> Optional[Dict[str, Any]]:
        """Update item sort order"""
        return await self.update(item_id, {"sort_order": sort_order})

