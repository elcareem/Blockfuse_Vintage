"""
Services package init.
"""
from app.services.auth_service import register_user, login_user
from app.services.product_service import get_all_products, get_product_by_id, create_product, update_product, delete_product
from app.services.cart_service import add_to_cart, update_cart_quantity, get_cart_items
from app.services.order_service import checkout, get_order_history
from app.services.cloudinary_service import upload_image, replace_image, delete_image

__all__ = [
    "register_user", "login_user",
    "get_all_products", "get_product_by_id", "create_product", "update_product", "delete_product",
    "add_to_cart", "update_cart_quantity", "get_cart_items",
    "checkout", "get_order_history",
    "upload_image", "replace_image", "delete_image",
]
