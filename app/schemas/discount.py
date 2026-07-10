"""Pydantic schemas for Discount request/response payloads."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.constants import CustomerTier, DiscountType


class DiscountBase(BaseModel):
    """Fields shared by create and update payloads.

    Includes cross-field validation to ensure that the fields required
    by a given ``type`` are actually supplied -- this keeps invalid
    discount configurations out of the database entirely, rather than
    failing later inside a strategy at calculation time.
    """

    name: str = Field(..., min_length=1, max_length=200)
    type: DiscountType
    value: float = Field(default=0.0, ge=0)
    minimum_purchase: float = Field(default=0.0, ge=0)
    is_stackable: bool = False
    priority: int = Field(default=100, ge=0)
    active: bool = True

    buy_quantity: int | None = Field(default=None, gt=0)
    get_quantity: int | None = Field(default=None, gt=0)
    applicable_category: str | None = Field(default=None, max_length=100)
    required_tier: CustomerTier | None = None
    coupon_code: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> "DiscountBase":
        """Ensure the fields required by ``type`` are present.

        Raises:
            ValueError: If a required field for the given discount
                type is missing.
        """

        if self.type == DiscountType.PERCENTAGE:
            if not (0 < self.value <= 100):
                raise ValueError("PERCENTAGE discount value must be between 0 and 100")
        elif self.type == DiscountType.FLAT:
            if self.value <= 0:
                raise ValueError("FLAT discount value must be greater than 0")
        elif self.type == DiscountType.BUY_X_GET_Y:
            if not self.buy_quantity or not self.get_quantity:
                raise ValueError(
                    "BUY_X_GET_Y discounts require both buy_quantity and get_quantity"
                )
        elif self.type == DiscountType.CATEGORY:
            if not self.applicable_category:
                raise ValueError("CATEGORY discounts require applicable_category")
            if not (0 < self.value <= 100):
                raise ValueError("CATEGORY discount value must be a percentage between 0 and 100")
        elif self.type == DiscountType.CUSTOMER_TIER:
            if not self.required_tier:
                raise ValueError("CUSTOMER_TIER discounts require required_tier")
            if not (0 < self.value <= 100):
                raise ValueError(
                    "CUSTOMER_TIER discount value must be a percentage between 0 and 100"
                )
        elif self.type == DiscountType.COUPON:
            if not self.coupon_code:
                raise ValueError("COUPON discounts require coupon_code")

        return self


class DiscountCreate(DiscountBase):
    """Payload for creating a new discount."""

    pass


class DiscountUpdate(BaseModel):
    """Payload for partially updating an existing discount.

    Note: cross-field validation is intentionally skipped for partial
    updates since not all fields are guaranteed to be present. The
    service layer re-validates the merged object before persisting.
    """

    name: str | None = Field(default=None, min_length=1, max_length=200)
    type: DiscountType | None = None
    value: float | None = Field(default=None, ge=0)
    minimum_purchase: float | None = Field(default=None, ge=0)
    is_stackable: bool | None = None
    priority: int | None = Field(default=None, ge=0)
    active: bool | None = None
    buy_quantity: int | None = Field(default=None, gt=0)
    get_quantity: int | None = Field(default=None, gt=0)
    applicable_category: str | None = Field(default=None, max_length=100)
    required_tier: CustomerTier | None = None
    coupon_code: str | None = Field(default=None, max_length=50)


class DiscountRead(DiscountBase):
    """Representation of a discount returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
