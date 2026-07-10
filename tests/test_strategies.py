"""Unit tests for each ``DiscountStrategy`` implementation.

These tests operate purely on in-memory model/dataclass instances (no
database, no HTTP) since the Strategy layer is deliberately decoupled
from persistence -- exactly the design property being verified here.
"""

from __future__ import annotations

from app.core.constants import CustomerTier, DiscountType
from app.models.customer import Customer
from app.models.discount import Discount
from app.models.product import Product
from app.strategies.base_strategy import CartContext, CartLine
from app.strategies.buy_x_get_y import BuyXGetYStrategy
from app.strategies.category_discount import CategoryDiscountStrategy
from app.strategies.coupon_discount import CouponDiscountStrategy
from app.strategies.customer_tier_discount import CustomerTierDiscountStrategy
from app.strategies.flat_discount import FlatDiscountStrategy
from app.strategies.percentage_discount import PercentageDiscountStrategy


def _customer(tier: CustomerTier = CustomerTier.SILVER) -> Customer:
    return Customer(id=1, name="Test Customer", email="test@example.com", tier=tier)


def _product(price: float, category: str = "General") -> Product:
    return Product(id=1, name="Test Product", category=category, price=price)


def test_percentage_discount_applies_when_minimum_met() -> None:
    discount = Discount(
        id=1, name="10% Off", type=DiscountType.PERCENTAGE, value=10, minimum_purchase=100
    )
    strategy = PercentageDiscountStrategy(discount)
    line = CartLine(product=_product(50), quantity=3, line_total=150)
    cart = CartContext(customer=_customer(), lines=[line], subtotal=150)

    result = strategy.calculate_discount(cart)

    assert result.applied is True
    assert result.amount == 15.0


def test_percentage_discount_not_applied_below_minimum() -> None:
    discount = Discount(
        id=1, name="10% Off", type=DiscountType.PERCENTAGE, value=10, minimum_purchase=500
    )
    strategy = PercentageDiscountStrategy(discount)
    cart = CartContext(customer=_customer(), lines=[], subtotal=100)

    result = strategy.calculate_discount(cart)

    assert result.applied is False
    assert result.amount == 0.0


def test_flat_discount_never_exceeds_subtotal() -> None:
    discount = Discount(
        id=1, name="Flat 200 Off", type=DiscountType.FLAT, value=200, minimum_purchase=0
    )
    strategy = FlatDiscountStrategy(discount)
    cart = CartContext(customer=_customer(), lines=[], subtotal=150)

    result = strategy.calculate_discount(cart)

    assert result.applied is True
    assert result.amount == 150.0  # capped at subtotal, not 200


def test_buy_x_get_y_grants_free_units_for_complete_groups() -> None:
    discount = Discount(
        id=1,
        name="Buy 2 Get 1 Free",
        type=DiscountType.BUY_X_GET_Y,
        buy_quantity=2,
        get_quantity=1,
        minimum_purchase=0,
    )
    strategy = BuyXGetYStrategy(discount)
    product = _product(price=100)
    # 6 units -> 2 complete groups of 3 -> 2 free units -> 200 discount
    line = CartLine(product=product, quantity=6, line_total=600)
    cart = CartContext(customer=_customer(), lines=[line], subtotal=600)

    result = strategy.calculate_discount(cart)

    assert result.applied is True
    assert result.amount == 200.0


def test_buy_x_get_y_not_applied_when_below_group_size() -> None:
    discount = Discount(
        id=1,
        name="Buy 2 Get 1 Free",
        type=DiscountType.BUY_X_GET_Y,
        buy_quantity=2,
        get_quantity=1,
        minimum_purchase=0,
    )
    strategy = BuyXGetYStrategy(discount)
    line = CartLine(product=_product(100), quantity=2, line_total=200)
    cart = CartContext(customer=_customer(), lines=[line], subtotal=200)

    result = strategy.calculate_discount(cart)

    assert result.applied is False


def test_category_discount_only_discounts_matching_lines() -> None:
    discount = Discount(
        id=1,
        name="Apparel 20% Off",
        type=DiscountType.CATEGORY,
        value=20,
        minimum_purchase=0,
        applicable_category="Apparel",
    )
    strategy = CategoryDiscountStrategy(discount)
    apparel_line = CartLine(product=_product(100, category="Apparel"), quantity=1, line_total=100)
    electronics_line = CartLine(
        product=_product(200, category="Electronics"), quantity=1, line_total=200
    )
    cart = CartContext(
        customer=_customer(), lines=[apparel_line, electronics_line], subtotal=300
    )

    result = strategy.calculate_discount(cart)

    assert result.applied is True
    assert result.amount == 20.0  # 20% of only the 100 apparel line


def test_customer_tier_discount_requires_sufficient_tier() -> None:
    discount = Discount(
        id=1,
        name="Gold+ 15% Off",
        type=DiscountType.CUSTOMER_TIER,
        value=15,
        minimum_purchase=0,
        required_tier=CustomerTier.GOLD,
    )
    strategy = CustomerTierDiscountStrategy(discount)

    silver_cart = CartContext(customer=_customer(CustomerTier.SILVER), lines=[], subtotal=100)
    gold_cart = CartContext(customer=_customer(CustomerTier.GOLD), lines=[], subtotal=100)
    platinum_cart = CartContext(customer=_customer(CustomerTier.PLATINUM), lines=[], subtotal=100)

    assert strategy.calculate_discount(silver_cart).applied is False
    assert strategy.calculate_discount(gold_cart).applied is True
    assert strategy.calculate_discount(platinum_cart).applied is True


def test_coupon_discount_requires_matching_code() -> None:
    discount = Discount(
        id=1,
        name="Welcome10",
        type=DiscountType.COUPON,
        value=10,
        minimum_purchase=0,
        coupon_code="WELCOME10",
    )
    strategy = CouponDiscountStrategy(discount)

    no_code_cart = CartContext(customer=_customer(), lines=[], subtotal=100, coupon_code=None)
    wrong_code_cart = CartContext(
        customer=_customer(), lines=[], subtotal=100, coupon_code="WRONG"
    )
    right_code_cart = CartContext(
        customer=_customer(), lines=[], subtotal=100, coupon_code="welcome10"
    )

    assert strategy.calculate_discount(no_code_cart).applied is False
    assert strategy.calculate_discount(wrong_code_cart).applied is False

    result = strategy.calculate_discount(right_code_cart)
    assert result.applied is True
    assert result.amount == 10.0
