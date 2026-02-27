"""
Alembic environment configuration.
Reads DATABASE_URL from the environment so it works both locally and inside Docker.
Imports all models via app.models so their metadata is registered with Base.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ─── Ensure the project root is on sys.path ──────────────────────────────────
# This allows `from app.xxx import ...` to work when running alembic from the
# project root or inside a Docker container (WORKDIR /app).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Alembic Config ──────────────────────────────────────────────────────────
config = context.config

# Override the sqlalchemy.url with the DATABASE_URL env var
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ─── Import all models so Alembic can see their metadata ─────────────────────
from app.database import Base  # noqa: E402
import app.models  # noqa: F401, E402 — registers all models with Base.metadata

target_metadata = Base.metadata


# ─── Offline mode ────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL without DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ─── Online mode ─────────────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Run migrations in 'online' mode (applies directly to the DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
