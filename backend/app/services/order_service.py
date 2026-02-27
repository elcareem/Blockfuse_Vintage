"""
Order service — checkout flow and order history.
"""
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order, OrderStatus
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.order import CheckoutRequest, OrderOut
from app.utils.exceptions import bad_request, not_found
from app.utils.logger import get_logger

logger = get_logger(__name__)


def checkout(db: Session, user: User, data: CheckoutRequest) -> list[OrderOut]:
    """
    Convert all cart items for a user into orders.
    Decrements stock, creates Transaction records, clears the cart.
    Returns a list of created order summaries.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    if not cart_items:
        raise bad_request("Your cart is empty")

    created_orders: list[OrderOut] = []

    for item in cart_items:
        product = item.product
        if product.stock_quantity < item.quantity:
            raise bad_request(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.stock_quantity}, requested: {item.quantity}"
            )

        unit_price = product.price
        amount = unit_price * item.quantity

        order = Order(
            product_id=product.id,
            user_id=user.id,
            amount=amount,
            quantity=item.quantity,
            unit_price=unit_price,
            order_status=OrderStatus.CONFIRMED,
        )
        db.add(order)
        db.flush()

        # Create a mock transaction record (extend with real payment gateway later)
        transaction = Transaction(
            order_id=order.id,
            payment_id=f"MOCK-{order.id:08d}",
        )
        db.add(transaction)

        # Decrement stock
        product.stock_quantity -= item.quantity

        created_orders.append(
            OrderOut(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=unit_price,
                amount=amount,
                status=OrderStatus.CONFIRMED,
                created_at=order.created_at,
            )
        )

        # Remove from cart
        db.delete(item)

    db.commit()
    logger.info(f"Checkout completed for user_id={user.id}, orders={len(created_orders)}")
    return created_orders


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
