"""
Inventory routes — product management with Cloudinary image handling (admin only).
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.product import ProductOut, ProductUpdate
from app.services.product_service import create_product, update_product, delete_product
from app.schemas.product import ProductCreate

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/product", response_model=ProductOut, status_code=201)
async def add_product(
    name: str = Form(...),
    description: str | None = Form(None),
    price: Decimal = Form(...),
    stock_quantity: int = Form(0),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Create a new product. Optionally upload a product image to Cloudinary.
    Requires admin authentication.
    Accepts multipart/form-data.
    """
    data = ProductCreate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
    )
    return create_product(db, data, image=image)


@router.put("/product/{product_id}", response_model=ProductOut)
async def edit_product(
    product_id: int,
    name: str | None = Form(None),
    description: str | None = Form(None),
    price: Decimal | None = Form(None),
    stock_quantity: int | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Update product fields and/or replace the product image on Cloudinary.
    Only provided fields are changed.
    """
    data = ProductUpdate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
    )
    return update_product(db, product_id, data, image=image)


@router.delete("/product/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Delete a product and its associated Cloudinary image.
    Requires admin authentication.
    """
    return delete_product(db, product_id)
