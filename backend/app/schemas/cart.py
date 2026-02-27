"""
Cart schemas — add and update cart items.
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal


class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1
    guest_id: str | None = None  # UUID string for unauthenticated users

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class CartUpdate(BaseModel):
    cart_id: int
    quantity: int
    guest_id: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: "ProductCartView"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductCartView(BaseModel):
    id: int
    name: str
    price: Decimal
    image_url: str | None

    model_config = {"from_attributes": True}


CartItemOut.model_rebuild()
