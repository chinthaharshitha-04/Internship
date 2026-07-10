"""API routes for the ``Promotion`` resource."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.promotion import PromotionCreate, PromotionRead
from app.services.promotion_service import PromotionService

router = APIRouter(prefix="/promotions", tags=["Promotions"])


def get_promotion_service(db: Session = Depends(get_db)) -> PromotionService:
    """FastAPI dependency that builds a ``PromotionService`` bound to a request-scoped session."""

    return PromotionService(db)


@router.post("", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
def create_promotion(
    payload: PromotionCreate, service: PromotionService = Depends(get_promotion_service)
) -> PromotionRead:
    """Schedule a new promotional window for a discount."""

    return service.create_promotion(payload)


@router.get("", response_model=list[PromotionRead])
def list_promotions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: PromotionService = Depends(get_promotion_service),
) -> list[PromotionRead]:
    """List all promotions, paginated."""

    return service.list_promotions(skip=skip, limit=limit)
