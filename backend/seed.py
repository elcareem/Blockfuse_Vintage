"""
Seed script — Populates the database with sample Blockfuse Vintage products.

Usage (inside Docker):
    docker compose exec app python seed.py

Usage (local):
    DATABASE_URL=mysql+pymysql://... python seed.py

Note: Cloudinary image_url values below are placeholder URLs.
Replace them with real Cloudinary secure_url values after uploading images,
or upload via POST /inventory/product using the API.
"""
import os
import sys
from decimal import Decimal

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Product  # ensures all tables are registered
from app.core.security import hash_password

SAMPLE_PRODUCTS = [
    {
        "name": "Classic Washed Tee — Navy",
        "description": "A perfectly worn-in heavyweight cotton tee. Pre-washed for that authentic vintage feel.",
        "price": Decimal("34.99"),
        "stock_quantity": 50,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
    {
        "name": "Retro Stripe Polo — Cream/Brown",
        "description": "70s-inspired stripe polo with a relaxed fit. 100% breathable cotton pique.",
        "price": Decimal("49.99"),
        "stock_quantity": 35,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
    {
        "name": "Faded Graphic Tee — Rust",
        "description": "Distressed vintage graphic print on a garment-dyed cotton tee. Every piece is unique.",
        "price": Decimal("39.99"),
        "stock_quantity": 40,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
    {
        "name": "Heritage Flannel Shirt — Red Plaid",
        "description": "Soft brushed flannel with a classic plaid pattern. Oversized for that vintage thrift store look.",
        "price": Decimal("64.99"),
        "stock_quantity": 25,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
    {
        "name": "Band Tee Reissue — Black",
        "description": "Premium reissue-style band graphic tee. Heavyweight 280gsm cotton with a worn-in pigment dye.",
        "price": Decimal("44.99"),
        "stock_quantity": 60,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
    {
        "name": "Washed Denim Shirt — Indigo",
        "description": "Overshirt in heavyweight washed denim. Works as a light jacket or layering piece.",
        "price": Decimal("74.99"),
        "stock_quantity": 20,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    },
]

ADMIN_USER = {
    "email": "admin@blockfusevintage.com",
    "username": "bfv_admin",
    "password": "Admin@1234",  # CHANGE THIS after seeding!
    "shipping_address": "Blockfuse HQ, Lagos, Nigeria",
    "is_admin": True,
}


def seed():
    db = SessionLocal()
    try:
        print("🌱 Seeding Blockfuse Vintage database...")

        # Create admin user if not already present
        existing_admin = db.query(User).filter(User.email == ADMIN_USER["email"]).first()
        if not existing_admin:
            from app.models.account import Account
            admin = User(
                email=ADMIN_USER["email"],
                username=ADMIN_USER["username"],
                password=hash_password(ADMIN_USER["password"]),
                shipping_address=ADMIN_USER["shipping_address"],
                is_admin=True,
            )
            db.add(admin)
            db.flush()
            db.add(Account(user_id=admin.id, balance=Decimal("0.00")))
            db.commit()
            print(f"  ✅ Admin user created: {ADMIN_USER['email']}")
        else:
            print(f"  ⏭  Admin user already exists: {ADMIN_USER['email']}")

        # Seed products
        seeded = 0
        for p in SAMPLE_PRODUCTS:
            exists = db.query(Product).filter(Product.name == p["name"]).first()
            if not exists:
                db.add(Product(**p))
                seeded += 1

        db.commit()
        print(f"  ✅ {seeded} product(s) seeded ({len(SAMPLE_PRODUCTS) - seeded} already existed)")
        print("\n🎉 Seeding complete!")
        print(f"\n⚠️  Admin credentials:")
        print(f"   Email:    {ADMIN_USER['email']}")
        print(f"   Password: {ADMIN_USER['password']}")
        print("   → CHANGE THIS PASSWORD after first login!\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
