"""
Database engine and session management.

This module wires up SQLAlchemy's engine, session factory, and the
declarative base that all ORM models inherit from. It also exposes a
``get_db`` generator function intended to be used as a FastAPI
dependency, giving every request its own isolated session.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# ``check_same_thread`` is only needed for SQLite, which by default
# disallows sharing a connection across threads. FastAPI's threaded
# request handling requires this to be disabled.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base class for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    The session is guaranteed to be closed after the request finishes,
    even if an exception is raised, preventing connection leaks.

    Yields:
        Session: An active SQLAlchemy ORM session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables registered on ``Base.metadata``.

    Importing the model modules is required before calling this so
    that each model class registers itself with ``Base.metadata``.
    """

    # Imported here (rather than at module level) to avoid circular
    # imports, since models import ``Base`` from this module.
    from app.models import (  # noqa: F401
        cart,
        cart_item,
        customer,
        discount,
        product,
        promotion,
    )

    Base.metadata.create_all(bind=engine)
