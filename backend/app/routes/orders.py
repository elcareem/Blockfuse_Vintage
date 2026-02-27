"""
Orders routes — checkout and order history (protected).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.order import CheckoutRequest, OrderOut
from app.services.order_service import checkout, get_order_history

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", response_model=list[OrderOut], status_code=201)
def place_order(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convert cart items into confirmed orders.
    Requires authentication.
    Decrements product stock and clears user's cart on success.
    """
    return checkout(db, current_user, data)


@router.get("/history", response_model=list[OrderOut])
def order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all past orders for the authenticated user.
    """
    return get_order_history(db, current_user.id)
