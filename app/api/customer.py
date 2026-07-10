"""API routes for the ``Customer`` resource."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    """FastAPI dependency that builds a ``CustomerService`` bound to a request-scoped session."""

    return CustomerService(db)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate, service: CustomerService = Depends(get_customer_service)
) -> CustomerRead:
    """Register a new customer."""

    return service.create_customer(payload)


@router.get("", response_model=list[CustomerRead])
def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: CustomerService = Depends(get_customer_service),
) -> list[CustomerRead]:
    """List customers, paginated."""

    return service.list_customers(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: int, service: CustomerService = Depends(get_customer_service)
) -> CustomerRead:
    """Fetch a single customer by id."""

    return service.get_customer(customer_id)


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    """Partially update an existing customer."""

    return service.update_customer(customer_id, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_customer(
    customer_id: int, service: CustomerService = Depends(get_customer_service)
) -> None:
    """Delete a customer."""

    service.delete_customer(customer_id)
