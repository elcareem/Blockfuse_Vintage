"""
Admin routes — read-only management views (admin only).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.schemas.user import UserOut
from app.schemas.order import OrderItemOut
from app.schemas.product import ProductOut

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserOut])
def admin_get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return all registered users."""
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/orders", response_model=list[OrderItemOut])
def admin_get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return all orders across all users."""
    return (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/products", response_model=list[ProductOut])
def admin_get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return all products including stock quantities."""
    return db.query(Product).offset(skip).limit(limit).all()
