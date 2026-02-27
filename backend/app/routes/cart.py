"""
Cart routes — public add-to-cart and quantity update.
Authenticated users are tracked by user_id.
Guests are tracked by UUID passed in the request body.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.cart import CartAdd, CartUpdate, CartItemOut
from app.services.cart_service import add_to_cart, update_cart_quantity, get_cart_items
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/cart", tags=["Cart"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/add", status_code=201)
def add_item_to_cart(
    data: CartAdd,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    Add a product to the cart.
    - If Authorization header is provided, links cart to authenticated user.
    - Otherwise, uses guest_id from the request body.
    """
    from app.core.security import decode_access_token

    user_id = None
    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except Exception:
            pass  # treat as guest if token is invalid

    cart_item = add_to_cart(db, data, user_id=user_id)
    return {"detail": "Item added to cart", "cart_id": cart_item.id}


@router.patch("/update-qty")
def update_quantity(
    data: CartUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    Update quantity of an existing cart item.
    Setting quantity to 0 removes the item.
    """
    from app.core.security import decode_access_token

    user_id = None
    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except Exception:
            pass

    result = update_cart_quantity(db, data, user_id=user_id)
    if isinstance(result, dict):
        return result
    return {"detail": "Quantity updated", "cart_id": result.id, "quantity": result.quantity}
