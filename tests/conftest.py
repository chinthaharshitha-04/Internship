"""Shared pytest fixtures.

Uses an in-memory SQLite database (isolated per test function) so the
suite runs fast and never touches the real ``retail_discount_engine.db``
file, while still exercising real SQLAlchemy models and queries rather
than mocks.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Yield a fresh in-memory SQLite session with all tables created.

    ``StaticPool`` ensures the same in-memory database is shared across
    connections within a test (SQLite's ``:memory:`` database is
    otherwise per-connection), while still giving each test function
    its own isolated database via the ``engine`` fixture recreation.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Yield a ``TestClient`` with the ``get_db`` dependency overridden.

    Overriding the dependency (rather than pointing the real app at a
    temp file) means every request in a test uses the same isolated,
    in-memory session as any direct ORM setup the test performs.
    """

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
