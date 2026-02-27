"""
Order service — checkout flow and order history.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order, OrderStatus
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.order import CheckoutRequest, OrderOut
from app.utils.exceptions import bad_request
from app.utils.logger import get_logger

logger = get_logger(__name__)


def checkout(db: Session, user: User, data: CheckoutRequest) -> list[OrderOut]:
    """
    Convert all cart items for a user into orders.
    Decrements stock, creates Transaction records, clears the cart.
    Returns a list of created order summaries.

    NOTE: `order.created_at` is a server-default (set by MySQL) and is
    None until after `db.commit()`. We collect all needed data upfront,
    commit once, then re-fetch rows so `created_at` is populated.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    if not cart_items:
        raise bad_request("Your cart is empty")

    # ── Validate stock before touching anything ───────────────────────────────
    lines = []
    for item in cart_items:
        product = item.product
        if product.stock_quantity < item.quantity:
            raise bad_request(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.stock_quantity}, requested: {item.quantity}"
            )
        lines.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": product.price,
            "amount": product.price * item.quantity,
            "cart_item": item,
            "product": product,
        })

    # ── Create orders, transactions, decrement stock, clear cart ─────────────
    order_ids: list[int] = []
    for line in lines:
        order = Order(
            product_id=line["product_id"],
            user_id=user.id,
            amount=line["amount"],
            quantity=line["quantity"],
            unit_price=line["unit_price"],
            order_status=OrderStatus.CONFIRMED,
        )
        db.add(order)
        db.flush()  # assigns order.id without committing

        db.add(Transaction(
            order_id=order.id,
            payment_id=f"MOCK-{order.id:08d}",
        ))

        line["product"].stock_quantity -= line["quantity"]
        db.delete(line["cart_item"])
        order_ids.append(order.id)

    db.commit()
    logger.info(f"Checkout completed for user_id={user.id}, {len(order_ids)} order(s) created")

    # ── Re-fetch after commit so server-generated created_at is populated ─────
    result = []
    for oid, line in zip(order_ids, lines):
        row = db.get(Order, oid)
        result.append(
            OrderOut(
                order_id=oid,
                product_id=line["product_id"],
                product_name=line["product_name"],
                quantity=line["quantity"],
                unit_price=line["unit_price"],
                amount=line["amount"],
                status=OrderStatus.CONFIRMED,
                created_at=row.created_at if row else datetime.now(timezone.utc),
            )
        )
    return result


def get_order_history(db: Session, user_id: int) -> list[OrderOut]:
    """
    Retrieve all orders for a user with product name included.
    """
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        OrderOut(
            order_id=o.id,
            product_id=o.product_id,
            product_name=o.product.name,
            quantity=o.quantity,
            unit_price=o.unit_price,
            amount=o.amount,
            status=o.order_status,
            created_at=o.created_at,
        )
        for o in orders
    ]
