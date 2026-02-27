"""
Order schemas — checkout and order history.
"""
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class CheckoutRequest(BaseModel):
    """Body for the checkout endpoint."""
    shipping_address: str | None = None  # override user's default address if provided


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    amount: Decimal
    order_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    amount: Decimal
    status: str
    created_at: datetime
