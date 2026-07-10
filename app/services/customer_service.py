"""Business logic orchestration for the ``Customer`` resource.

Services sit between API routers and repositories: routers translate
HTTP <-> Pydantic schemas, repositories translate Python <-> SQL, and
services own the business rules that don't belong in either. This
keeps each layer testable in isolation (Clean Architecture).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.custom_exception import DuplicateResourceException, NotFoundException
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Encapsulates business rules for creating and managing customers."""

    def __init__(self, db: Session) -> None:
        self.repository = CustomerRepository(db)

    def create_customer(self, payload: CustomerCreate) -> Customer:
        """Create a new customer, enforcing email uniqueness.

        Args:
            payload: Validated customer creation data.

        Returns:
            Customer: The newly persisted customer.

        Raises:
            DuplicateResourceException: If the email is already in use.
        """

        existing = self.repository.get_by_email(payload.email)
        if existing is not None:
            raise DuplicateResourceException(
                f"A customer with email '{payload.email}' already exists."
            )

        customer = Customer(name=payload.name, email=payload.email, tier=payload.tier)
        return self.repository.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        """Fetch a customer by id.

        Raises:
            NotFoundException: If no such customer exists.
        """

        customer = self.repository.get_by_id(customer_id)
        if customer is None:
            raise NotFoundException(f"Customer with id {customer_id} not found.")
        return customer

    def list_customers(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        """Return a paginated list of customers."""

        return self.repository.list_all(skip=skip, limit=limit)

    def update_customer(self, customer_id: int, payload: CustomerUpdate) -> Customer:
        """Apply a partial update to an existing customer.

        Raises:
            NotFoundException: If no such customer exists.
            DuplicateResourceException: If updating to an email that
                belongs to a different customer.
        """

        customer = self.get_customer(customer_id)

        if payload.email is not None and payload.email != customer.email:
            existing = self.repository.get_by_email(payload.email)
            if existing is not None and existing.id != customer_id:
                raise DuplicateResourceException(
                    f"A customer with email '{payload.email}' already exists."
                )
            customer.email = payload.email

        if payload.name is not None:
            customer.name = payload.name
        if payload.tier is not None:
            customer.tier = payload.tier

        return self.repository.update(customer)

    def delete_customer(self, customer_id: int) -> None:
        """Delete a customer.

        Raises:
            NotFoundException: If no such customer exists.
        """

        customer = self.get_customer(customer_id)
        self.repository.delete(customer)
