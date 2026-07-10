"""Repository for ``Product`` persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    """Data-access layer for the ``Product`` entity."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, product: Product) -> Product:
        """Persist a new product."""

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        """Fetch a product by primary key, or ``None`` if not found."""

        return self.db.get(Product, product_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Return a paginated list of all products."""

        stmt = select(Product).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_by_category(self, category: str) -> list[Product]:
        """Return all products belonging to a given category."""

        stmt = select(Product).where(Product.category == category)
        return list(self.db.scalars(stmt).all())

    def update(self, product: Product) -> Product:
        """Persist changes made to an already-tracked ``Product``."""

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        """Delete a product."""

        self.db.delete(product)
        self.db.commit()
