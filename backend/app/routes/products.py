"""
Products routes — public catalog browsing.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.product import ProductOut
from app.services.product_service import get_all_products, get_product_by_id

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """List all available products (paginated)."""
    return get_all_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a single product."""
    return get_product_by_id(db, product_id)
