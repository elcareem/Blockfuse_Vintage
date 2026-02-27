"""
Transaction schemas.
"""
from pydantic import BaseModel
from datetime import datetime


class TransactionOut(BaseModel):
    id: int
    order_id: int
    payment_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
