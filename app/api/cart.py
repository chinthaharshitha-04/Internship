"""API routes for cart price calculation."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.bill import BillResponse
from app.schemas.cart import CartCalculateRequest
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    """FastAPI dependency that builds a ``CartService`` bound to a request-scoped session."""

    return CartService(db)


@router.post("/calculate", response_model=BillResponse)
def calculate_cart(
    payload: CartCalculateRequest, service: CartService = Depends(get_cart_service)
) -> BillResponse:
    """Price a cart, applying every eligible promotion and returning the final bill.

    Evaluates all active, in-window promotions against the supplied
    cart, combines stackable discounts, selects the best single
    non-stackable discount by priority, and returns the subtotal,
    applied discount breakdown, total discount, and final payable
    amount.
    """

    return service.calculate(payload)
