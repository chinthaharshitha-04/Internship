"""Pydantic schemas for Product request/response payloads."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Fields shared by create and update payloads."""

    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Unit price, must be greater than zero")


class ProductCreate(ProductBase):
    """Payload for creating a new product."""

    pass


class ProductUpdate(BaseModel):
    """Payload for partially updating an existing product."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)


class ProductRead(ProductBase):
    """Representation of a product returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
