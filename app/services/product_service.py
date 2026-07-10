"""Business logic orchestration for the ``Product`` resource."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.custom_exception import NotFoundException
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.validators.product_validator import ProductValidator


class ProductService:
    """Encapsulates business rules for creating and managing products."""

    def __init__(self, db: Session) -> None:
        self.repository = ProductRepository(db)

    def create_product(self, payload: ProductCreate) -> Product:
        """Create a new product.

        Args:
            payload: Validated product creation data. Pydantic already
                enforces ``price > 0`` via the schema's ``gt=0``
                constraint; ``ProductValidator`` adds the reusable,
                unit-testable business-rule checks on top of that.

        Returns:
            Product: The newly persisted product.
        """

        ProductValidator.validate_price(payload.price)
        ProductValidator.validate_category(payload.category)

        product = Product(name=payload.name, category=payload.category, price=payload.price)
        return self.repository.create(product)

    def get_product(self, product_id: int) -> Product:
        """Fetch a product by id.

        Raises:
            NotFoundException: If no such product exists.
        """

        product = self.repository.get_by_id(product_id)
        if product is None:
            raise NotFoundException(f"Product with id {product_id} not found.")
        return product

    def list_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Return a paginated list of products."""

        return self.repository.list_all(skip=skip, limit=limit)

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        """Apply a partial update to an existing product.

        Raises:
            NotFoundException: If no such product exists.
        """

        product = self.get_product(product_id)

        if payload.name is not None:
            product.name = payload.name
        if payload.category is not None:
            ProductValidator.validate_category(payload.category)
            product.category = payload.category
        if payload.price is not None:
            ProductValidator.validate_price(payload.price)
            product.price = payload.price

        return self.repository.update(product)

    def delete_product(self, product_id: int) -> None:
        """Delete a product.

        Raises:
            NotFoundException: If no such product exists.
        """

        product = self.get_product(product_id)
        self.repository.delete(product)
