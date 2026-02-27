"""
Authentication service — register and login.
"""
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.account import Account
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.exceptions import conflict, unauthorized
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_user(db: Session, data: RegisterRequest) -> User:
    """
    Create a new user and automatically provision an account wallet.
    Raises 409 if email or username already exists.
    """
    if db.query(User).filter(User.email == data.email).first():
        raise conflict("Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise conflict("Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        shipping_address=data.shipping_address,
    )
    db.add(user)
    db.flush()  # get user.id without committing

    # Automatically create linked account
    account = Account(user_id=user.id, balance=0.00)
    db.add(account)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email} (id={user.id})")
    return user


def login_user(db: Session, data: LoginRequest) -> TokenResponse:
    """
    Authenticate a user by email + password and return a JWT.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise unauthorized("Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(access_token=token)
