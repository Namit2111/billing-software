"""API v1 Router"""
from fastapi import APIRouter

from app.api.v1 import auth, clients, products, invoices, reports, settings, dashboard

router = APIRouter()

# Include all routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(clients.router, prefix="/clients", tags=["Clients"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
router.include_router(settings.router, prefix="/settings", tags=["Settings"])

