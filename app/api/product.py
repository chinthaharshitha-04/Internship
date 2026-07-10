"""API routes for the ``Product`` resource."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """FastAPI dependency that builds a ``ProductService`` bound to a request-scoped session."""

    return ProductService(db)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate, service: ProductService = Depends(get_product_service)
) -> ProductRead:
    """Add a new product to the catalogue."""

    return service.create_product(payload)


@router.get("", response_model=list[ProductRead])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: ProductService = Depends(get_product_service),
) -> list[ProductRead]:
    """List products, paginated."""

    return service.list_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int, service: ProductService = Depends(get_product_service)
) -> ProductRead:
    """Fetch a single product by id."""

    return service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    """Partially update an existing product."""

    return service.update_product(product_id, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_product(
    product_id: int, service: ProductService = Depends(get_product_service)
) -> None:
    """Delete a product."""

    service.delete_product(product_id)
