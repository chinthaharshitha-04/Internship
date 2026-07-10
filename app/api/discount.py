"""API routes for the ``Discount`` resource."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discount import DiscountCreate, DiscountRead, DiscountUpdate
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["Discounts"])


def get_discount_service(db: Session = Depends(get_db)) -> DiscountService:
    """FastAPI dependency that builds a ``DiscountService`` bound to a request-scoped session."""

    return DiscountService(db)


@router.post("", response_model=DiscountRead, status_code=status.HTTP_201_CREATED)
def create_discount(
    payload: DiscountCreate, service: DiscountService = Depends(get_discount_service)
) -> DiscountRead:
    """Create a new discount rule."""

    return service.create_discount(payload)


@router.get("", response_model=list[DiscountRead])
def list_discounts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: DiscountService = Depends(get_discount_service),
) -> list[DiscountRead]:
    """List discount rules, paginated."""

    return service.list_discounts(skip=skip, limit=limit)


@router.get("/{discount_id}", response_model=DiscountRead)
def get_discount(
    discount_id: int, service: DiscountService = Depends(get_discount_service)
) -> DiscountRead:
    """Fetch a single discount rule by id."""

    return service.get_discount(discount_id)


@router.put("/{discount_id}", response_model=DiscountRead)
def update_discount(
    discount_id: int,
    payload: DiscountUpdate,
    service: DiscountService = Depends(get_discount_service),
) -> DiscountRead:
    """Partially update an existing discount rule."""

    return service.update_discount(discount_id, payload)


@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_discount(
    discount_id: int, service: DiscountService = Depends(get_discount_service)
) -> None:
    """Delete a discount rule."""

    service.delete_discount(discount_id)
