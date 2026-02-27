"""
Cloudinary service — upload, replace, and delete product images.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import bad_request

logger = get_logger(__name__)

# Configure Cloudinary once at import time
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

FOLDER = "blockfuse_vintage/products"


def upload_image(file: UploadFile) -> dict:
    """
    Upload an image to Cloudinary.
    Returns dict with 'secure_url' and 'public_id'.
    """
    try:
        contents = file.file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder=FOLDER,
            resource_type="image",
            overwrite=True,
        )
        logger.info(f"Uploaded image: {result['public_id']}")
        return {"secure_url": result["secure_url"], "public_id": result["public_id"]}
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise bad_request(f"Image upload failed: {str(e)}")


def replace_image(public_id: str, file: UploadFile) -> dict:
    """
    Replace an existing Cloudinary image by its public_id.
    Deletes old image first, then uploads new one.
    """
    try:
        delete_image(public_id)
    except Exception:
        pass  # Don't abort if old image was already deleted
    return upload_image(file)


def delete_image(public_id: str) -> None:
    """
    Delete an image from Cloudinary by its public_id.
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        logger.info(f"Deleted Cloudinary image: {public_id} → {result.get('result')}")
    except Exception as e:
        logger.error(f"Cloudinary delete failed for {public_id}: {e}")
