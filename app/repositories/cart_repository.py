"""Repository for ``Cart`` / ``CartItem`` persistence operations."""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:
    """Data-access layer for the ``Cart`` and ``CartItem`` entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, cart: Cart) -> Cart:
        """Persist a new cart together with its items.

        Args:
            cart: A transient ``Cart`` instance, typically constructed
                with its ``items`` relationship already populated.

        Returns:
            Cart: The persisted cart, eagerly loaded with items and
            each item's product, so the Pricing Engine can compute
            prices without additional queries.
        """

        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_by_id(self, cart_id: int) -> Cart | None:
        """Fetch a cart by primary key, eagerly loading items and products."""

        stmt_options = joinedload(Cart.items).joinedload(CartItem.product)
        return (
            self.db.query(Cart)
            .options(stmt_options)
            .filter(Cart.id == cart_id)
            .first()
        )
