"""Pydantic schemas for Customer request/response payloads."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import CustomerTier


class CustomerBase(BaseModel):
    """Fields shared by create and update payloads."""

    name: str = Field(..., min_length=1, max_length=120, description="Customer's full name")
    email: EmailStr = Field(..., description="Unique email address")
    tier: CustomerTier = Field(
        default=CustomerTier.SILVER, description="Loyalty tier"
    )


class CustomerCreate(CustomerBase):
    """Payload for creating a new customer."""

    pass


class CustomerUpdate(BaseModel):
    """Payload for partially updating an existing customer.

    All fields are optional so callers can update a single attribute
    (e.g. just the tier) without resending the whole object.
    """

    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    tier: CustomerTier | None = None


class CustomerRead(CustomerBase):
    """Representation of a customer returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
