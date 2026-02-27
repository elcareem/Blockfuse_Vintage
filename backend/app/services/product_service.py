"""
Product service — catalog CRUD with Cloudinary image management.
"""
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.cloudinary_service import upload_image, replace_image, delete_image
from app.utils.exceptions import not_found
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_all_products(db: Session, skip: int = 0, limit: int = 50) -> list[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise not_found(f"Product {product_id} not found")
    return product


def create_product(
    db: Session,
    data: ProductCreate,
    image: UploadFile | None = None,
) -> Product:
    image_url = None
    public_id = None

    if image:
        result = upload_image(image)
        image_url = result["secure_url"]
        public_id = result["public_id"]

    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock_quantity=data.stock_quantity,
        image_url=image_url,
        cloudinary_public_id=public_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"Product created: {product.name} (id={product.id})")
    return product


def update_product(
    db: Session,
    product_id: int,
    data: ProductUpdate,
    image: UploadFile | None = None,
) -> Product:
    product = get_product_by_id(db, product_id)

    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.stock_quantity is not None:
        product.stock_quantity = data.stock_quantity

    if image:
        result = replace_image(product.cloudinary_public_id or "", image)
        product.image_url = result["secure_url"]
        product.cloudinary_public_id = result["public_id"]

    db.commit()
    db.refresh(product)
    logger.info(f"Product updated: id={product_id}")
    return product


def delete_product(db: Session, product_id: int) -> dict:
    product = get_product_by_id(db, product_id)

    if product.cloudinary_public_id:
        delete_image(product.cloudinary_public_id)

    db.delete(product)
    db.commit()
    logger.info(f"Product deleted: id={product_id}")
    return {"detail": f"Product {product_id} deleted successfully"}
