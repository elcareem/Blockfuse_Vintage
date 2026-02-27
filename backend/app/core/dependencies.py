"""
FastAPI dependencies — DB session, current user, admin guard.
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.utils.exceptions import unauthorized, forbidden, not_found

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate the Bearer JWT from the Authorization header.
    Returns the authenticated User ORM object.
    """
    if credentials is None:
        raise unauthorized("Authorization header missing")

    payload = decode_access_token(credentials.credentials)
    user_id: int = payload.get("sub")

    user = db.get(User, int(user_id))
    if not user:
        raise not_found("User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Extends get_current_user — additionally checks is_admin flag.
    """
    if not current_user.is_admin:
        raise forbidden("Admin privileges required")
    return current_user
