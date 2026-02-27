"""
Product schemas — catalog CRUD.
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock_quantity: int = 0

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock quantity cannot be negative")
        return v


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    image_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
