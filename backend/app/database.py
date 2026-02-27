"""
SQLAlchemy engine, session factory, and declarative base.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# ─── Engine ──────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # detect stale connections
    pool_size=10,                # connection pool size
    max_overflow=20,             # extra connections beyond pool_size
    pool_recycle=3600,           # recycle connections every 1 hour
    echo=False,                  # set True only for SQL debugging
)

# ─── Session Factory ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─── Declarative Base ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Dependency ──────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a database session and ensures
    it is properly closed after the request, even on errors.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
