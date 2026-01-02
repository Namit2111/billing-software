"""
Invoice service
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from supabase import Client

from app.repositories.invoice import InvoiceRepository, InvoiceItemRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.client import ClientRepository
from app.core.exceptions import NotFoundError, InvoiceError, ForbiddenError


class InvoiceService:
    """Service for invoice operations"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.invoice_repo = InvoiceRepository(supabase)
        self.item_repo = InvoiceItemRepository(supabase)
        self.org_repo = OrganizationRepository(supabase)
        self.client_repo = ClientRepository(supabase)
    
    async def create(
        self,
        organization_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new invoice
        
        Args:
            organization_id: Organization UUID
            user_id: Creating user ID
            data: Invoice data with items
            
        Returns:
            Created invoice with items
        """
        # Verify client exists and belongs to organization
        client = await self.client_repo.get_by_id(data["client_id"])
        if not client or client.get("organization_id") != organization_id:
            raise NotFoundError("Client", data["client_id"])
        
        # Get organization for invoice number
        org = await self.org_repo.get_by_id(organization_id)
        invoice_number = await self.org_repo.get_next_invoice_number(organization_id)
        
        # Calculate due date if not provided
        issue_date = data.get("issue_date", date.today())
        if isinstance(issue_date, str):
            issue_date = date.fromisoformat(issue_date)
        
        due_date = data.get("due_date")
        if not due_date:
            payment_terms = org.get("default_payment_terms", 30)
            due_date = issue_date + timedelta(days=payment_terms)
        elif isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        
        # Extract items
        items_data = data.pop("items", [])
        
        # Calculate totals
        subtotal = 0
        tax_total = 0
        discount_total = 0
        
        for item in items_data:
            item_subtotal = item["quantity"] * item["unit_price"]
            item_discount = item_subtotal * (item.get("discount_percent", 0) / 100)
            item_taxable = item_subtotal - item_discount
            item_tax = item_taxable * (item.get("tax_rate", 0) / 100)
            
            subtotal += item_subtotal
            discount_total += item_discount
            tax_total += item_tax
        
        total = subtotal - discount_total + tax_total
        
        # Create invoice
        invoice_data = {
            "organization_id": organization_id,
            "client_id": data["client_id"],
            "invoice_number": invoice_number,
            "status": "draft",
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "currency": data.get("currency", client.get("currency", "USD")),
            "subtotal": subtotal,
            "tax_total": tax_total,
            "discount_total": discount_total,
            "total": total,
            "amount_paid": 0,
            "notes": data.get("notes"),
            "terms": data.get("terms"),
            "footer": data.get("footer"),
            "created_by": user_id
        }
        
        invoice = await self.invoice_repo.create(invoice_data)
        
        # Increment organization invoice number
        await self.org_repo.increment_invoice_number(organization_id)
        
        # Create line items
        if items_data:
            for i, item in enumerate(items_data):
                item["invoice_id"] = invoice["id"]
                item["sort_order"] = i
            
            items = await self.item_repo.create_bulk(items_data)
            invoice["items"] = items
        else:
            invoice["items"] = []
        
        # Add client data
        invoice["client"] = client
        
        # Add computed fields
        invoice["balance_due"] = invoice["total"] - invoice.get("amount_paid", 0)
        
        # Add item computed fields
        for item in invoice.get("items", []):
            subtotal = item["quantity"] * item["unit_price"]
            discount = subtotal * (item.get("discount_percent", 0) / 100)
            taxable = subtotal - discount
            tax = taxable * (item.get("tax_rate", 0) / 100)
            
            item["subtotal"] = subtotal - discount
            item["tax_amount"] = tax
            item["total"] = subtotal - discount + tax
        
        return invoice
    
    async def get(
        self,
        invoice_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get invoice with items and client"""
        invoice = await self.invoice_repo.get_by_id_with_items(invoice_id)
        
        if not invoice or invoice.get("organization_id") != organization_id:
            raise NotFoundError("Invoice", invoice_id)
        
        # Calculate computed fields
        invoice["balance_due"] = invoice["total"] - invoice.get("amount_paid", 0)
        
        # Add item computed fields
        for item in invoice.get("items", []):
            subtotal = item["quantity"] * item["unit_price"]
            discount = subtotal * (item.get("discount_percent", 0) / 100)
            taxable = subtotal - discount
            tax = taxable * (item.get("tax_rate", 0) / 100)
            
            item["subtotal"] = subtotal - discount
            item["tax_amount"] = tax
            item["total"] = subtotal - discount + tax
        
        return invoice
    
    async def update(
        self,
        invoice_id: str,
        organization_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update invoice"""
        invoice = await self.get(invoice_id, organization_id)
        
        # Only drafts can be edited
        if invoice.get("status") != "draft":
            raise InvoiceError("Only draft invoices can be edited")
        
        # Handle client change
        if data.get("client_id") and data["client_id"] != invoice["client_id"]:
            client = await self.client_repo.get_by_id(data["client_id"])
            if not client or client.get("organization_id") != organization_id:
                raise NotFoundError("Client", data["client_id"])
        
        # Convert dates to ISO format
        if "issue_date" in data and isinstance(data["issue_date"], date):
            data["issue_date"] = data["issue_date"].isoformat()
        if "due_date" in data and isinstance(data["due_date"], date):
            data["due_date"] = data["due_date"].isoformat()
        
        updated = await self.invoice_repo.update(invoice_id, data)
        return await self.get(invoice_id, organization_id)
    
    async def delete(
        self,
        invoice_id: str,
        organization_id: str
    ) -> bool:
        """Delete invoice (only drafts can be deleted)"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") != "draft":
            raise InvoiceError("Only draft invoices can be deleted")
        
        # Delete items first
        await self.item_repo.delete_by_invoice(invoice_id)
        
        # Delete invoice
        await self.invoice_repo.delete(invoice_id)
        return True
    
    async def add_item(
        self,
        invoice_id: str,
        organization_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add item to invoice"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") != "draft":
            raise InvoiceError("Only draft invoices can be edited")
        
        # Get current item count for sort order
        items = await self.item_repo.get_by_invoice(invoice_id)
        item_data["invoice_id"] = invoice_id
        item_data["sort_order"] = len(items)
        
        item = await self.item_repo.create(item_data)
        
        # Recalculate totals
        await self._recalculate_totals(invoice_id)
        
        return item
    
    async def update_item(
        self,
        invoice_id: str,
        item_id: str,
        organization_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update invoice item"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") != "draft":
            raise InvoiceError("Only draft invoices can be edited")
        
        item = await self.item_repo.update(item_id, item_data)
        
        # Recalculate totals
        await self._recalculate_totals(invoice_id)
        
        return item
    
    async def delete_item(
        self,
        invoice_id: str,
        item_id: str,
        organization_id: str
    ) -> bool:
        """Delete invoice item"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") != "draft":
            raise InvoiceError("Only draft invoices can be edited")
        
        await self.item_repo.delete(item_id)
        
        # Recalculate totals
        await self._recalculate_totals(invoice_id)
        
        return True
    
    async def _recalculate_totals(self, invoice_id: str) -> None:
        """Recalculate invoice totals from items"""
        items = await self.item_repo.get_by_invoice(invoice_id)
        
        subtotal = 0
        tax_total = 0
        discount_total = 0
        
        for item in items:
            item_subtotal = item["quantity"] * item["unit_price"]
            item_discount = item_subtotal * (item.get("discount_percent", 0) / 100)
            item_taxable = item_subtotal - item_discount
            item_tax = item_taxable * (item.get("tax_rate", 0) / 100)
            
            subtotal += item_subtotal
            discount_total += item_discount
            tax_total += item_tax
        
        total = subtotal - discount_total + tax_total
        
        await self.invoice_repo.update(invoice_id, {
            "subtotal": subtotal,
            "tax_total": tax_total,
            "discount_total": discount_total,
            "total": total
        })
    
    async def mark_as_sent(
        self,
        invoice_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Mark invoice as sent"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") not in ["draft"]:
            raise InvoiceError("Invoice has already been sent")
        
        if not invoice.get("items") or len(invoice["items"]) == 0:
            raise InvoiceError("Cannot send invoice without line items")
        
        await self.invoice_repo.mark_as_sent(invoice_id)
        return await self.get(invoice_id, organization_id)
    
    async def mark_as_paid(
        self,
        invoice_id: str,
        organization_id: str,
        amount_paid: Optional[float] = None,
        paid_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Mark invoice as paid"""
        invoice = await self.get(invoice_id, organization_id)
        
        if invoice.get("status") == "paid":
            raise InvoiceError("Invoice is already marked as paid")
        
        if invoice.get("status") == "draft":
            raise InvoiceError("Cannot mark draft invoice as paid")
        
        # Use invoice total if amount not specified
        if amount_paid is None:
            amount_paid = invoice["total"]
        
        await self.invoice_repo.mark_as_paid(invoice_id, amount_paid, paid_at)
        return await self.get(invoice_id, organization_id)
    
    async def list(
        self,
        organization_id: str,
        status: Optional[str] = None,
        client_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List invoices with pagination"""
        offset = (page - 1) * per_page
        
        filters = {}
        if status:
            filters["status"] = status
        if client_id:
            filters["client_id"] = client_id
        
        invoices = await self.invoice_repo.get_all(
            organization_id,
            filters=filters if filters else None,
            limit=per_page,
            offset=offset
        )
        
        total = await self.invoice_repo.count(organization_id, filters if filters else None)
        total_pages = (total + per_page - 1) // per_page
        
        # Add client names
        for inv in invoices:
            if inv.get("client_id"):
                client = await self.client_repo.get_by_id(inv["client_id"])
                inv["client_name"] = client.get("name", "") if client else ""
            inv["balance_due"] = inv["total"] - inv.get("amount_paid", 0)
        
        return {
            "invoices": invoices,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    async def get_overdue(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all overdue invoices"""
        return await self.invoice_repo.get_overdue(organization_id)
    
    async def update_overdue_status(self, organization_id: str) -> int:
        """Update status of overdue invoices"""
        overdue = await self.invoice_repo.get_overdue(organization_id)
        count = 0
        
        for inv in overdue:
            if inv.get("status") == "sent":
                await self.invoice_repo.update_status(inv["id"], "overdue")
                count += 1
        
        return count

