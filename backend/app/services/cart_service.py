"""
Cart service — add items and adjust quantities for users and guests.
"""
import uuid
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.guest import Guest
from app.schemas.cart import CartAdd, CartUpdate
from app.services.product_service import get_product_by_id
from app.utils.exceptions import not_found, bad_request
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_or_create_guest(db: Session, guest_id_str: str | None) -> Guest | None:
    """Find existing guest row or create a new one."""
    if guest_id_str is None:
        return None
    guest = db.query(Guest).filter(Guest.guest_id == guest_id_str).first()
    if not guest:
        guest = Guest(guest_id=guest_id_str)
        db.add(guest)
        db.flush()
    return guest


def add_to_cart(db: Session, data: CartAdd, user_id: int | None = None) -> Cart:
    """
    Add a product to cart.
    - Authenticated users: linked by user_id
    - Guests: linked by UUID guest_id (auto-created if new)
    If item already exists, increment quantity.
    """
    product = get_product_by_id(db, data.product_id)

    if data.quantity > product.stock_quantity:
        raise bad_request(
            f"Requested quantity ({data.quantity}) exceeds available stock ({product.stock_quantity})"
        )

    guest = None
    if user_id is None:
        if not data.guest_id:
            # Auto-generate a guest UUID
            data.guest_id = str(uuid.uuid4())
        guest = _get_or_create_guest(db, data.guest_id)

    # Check for existing cart item
    query = db.query(Cart).filter(Cart.product_id == data.product_id)
    if user_id:
        query = query.filter(Cart.user_id == user_id)
    elif guest:
        query = query.filter(Cart.guest_id == guest.id)

    existing = query.first()
    if existing:
        existing.quantity += data.quantity
        db.commit()
        db.refresh(existing)
        return existing

    cart_item = Cart(
        user_id=user_id,
        guest_id=guest.id if guest else None,
        product_id=data.product_id,
        quantity=data.quantity,
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    logger.info(f"Cart item added: product_id={data.product_id}, user_id={user_id}")
    return cart_item


def update_cart_quantity(
    db: Session, data: CartUpdate, user_id: int | None = None
) -> Cart | dict:
    """
    Update quantity of a cart item.
    If quantity is 0, remove the item.
    """
    cart_item = db.get(Cart, data.cart_id)
    if not cart_item:
        raise not_found("Cart item not found")

    # Ownership check
    if user_id and cart_item.user_id != user_id:
        raise not_found("Cart item not found")

    if data.quantity == 0:
        db.delete(cart_item)
        db.commit()
        return {"detail": "Cart item removed"}

    cart_item.quantity = data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def get_cart_items(db: Session, user_id: int) -> list[Cart]:
    return (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .all()
    )
