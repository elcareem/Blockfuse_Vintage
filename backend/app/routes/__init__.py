"""
Routes package init — collect all routers.
"""
from app.routes.auth import router as auth_router
from app.routes.products import router as products_router
from app.routes.cart import router as cart_router
from app.routes.orders import router as orders_router
from app.routes.admin import router as admin_router
from app.routes.inventory import router as inventory_router

__all__ = [
    "auth_router",
    "products_router",
    "cart_router",
    "orders_router",
    "admin_router",
    "inventory_router",
]
