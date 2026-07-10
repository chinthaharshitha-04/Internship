"""
Application-wide constants and enumerations.

Centralizing these values avoids magic strings scattered across the
codebase and gives us a single source of truth for valid discount
types, customer tiers, and product categories.
"""

from enum import Enum


class DiscountType(str, Enum):
    """Supported discount strategy types.

    The value of each member is used as the discriminator that the
    ``StrategyFactory`` uses to instantiate the correct
    ``DiscountStrategy`` implementation.
    """

    PERCENTAGE = "PERCENTAGE"
    FLAT = "FLAT"
    BUY_X_GET_Y = "BUY_X_GET_Y"
    CATEGORY = "CATEGORY"
    CUSTOMER_TIER = "CUSTOMER_TIER"
    COUPON = "COUPON"


class CustomerTier(str, Enum):
    """Loyalty tiers a customer can belong to."""

    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class ErrorCode(str, Enum):
    """Application-level error codes returned in error responses."""

    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Business rule constants
MIN_QUANTITY = 1
MIN_PRICE = 0.01
DEFAULT_CURRENCY = "INR"

# Tier hierarchy used for comparisons (e.g. "at least Gold").
TIER_RANK = {
    CustomerTier.SILVER: 1,
    CustomerTier.GOLD: 2,
    CustomerTier.PLATINUM: 3,
}
