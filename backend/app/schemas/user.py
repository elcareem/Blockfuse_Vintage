"""
User schemas — public representation and updates.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    shipping_address: str | None
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str | None = None
    shipping_address: str | None = None


class UserAdminOut(UserOut):
    """Extended view for admin endpoints."""
    pass
