"""Repository for ``Customer`` persistence operations.

The Repository Pattern isolates SQLAlchemy query construction from
business logic. Services depend on this class's interface, not on
SQLAlchemy directly, which makes the service layer easy to unit test
with fakes/mocks and keeps ORM concerns out of business rules.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    """Data-access layer for the ``Customer`` entity."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, customer: Customer) -> Customer:
        """Persist a new customer.

        Args:
            customer: A transient ``Customer`` instance to save.

        Returns:
            Customer: The persisted instance, with its ``id`` populated.
        """

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        """Fetch a customer by primary key, or ``None`` if not found."""

        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        """Fetch a customer by their unique email address."""

        stmt = select(Customer).where(Customer.email == email)
        return self.db.scalars(stmt).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        """Return a paginated list of all customers."""

        stmt = select(Customer).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def update(self, customer: Customer) -> Customer:
        """Persist changes made to an already-tracked ``Customer``."""

        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete a customer and cascade-delete their carts."""

        self.db.delete(customer)
        self.db.commit()
