"""Tests for ``RuleEngine`` (stacking/priority resolution) and ``StrategyFactory``."""

from __future__ import annotations

import pytest

from app.core.constants import DiscountType
from app.engine.rule_engine import RuleEngine
from app.engine.strategy_factory import StrategyFactory
from app.exceptions.custom_exception import BadRequestException
from app.models.discount import Discount
from app.strategies.base_strategy import DiscountResult
from app.strategies.percentage_discount import PercentageDiscountStrategy


def _result(discount: Discount, amount: float, applied: bool = True) -> DiscountResult:
    return DiscountResult(discount=discount, amount=amount, applied=applied)


def test_rule_engine_combines_all_stackable_discounts() -> None:
    d1 = Discount(id=1, name="Stack A", type=DiscountType.PERCENTAGE, is_stackable=True)
    d2 = Discount(id=2, name="Stack B", type=DiscountType.FLAT, is_stackable=True)

    outcome = RuleEngine().resolve([_result(d1, 10.0), _result(d2, 20.0)])

    assert len(outcome.selected) == 2
    assert outcome.total_discount == 30.0


def test_rule_engine_picks_best_non_stackable_by_priority() -> None:
    high_priority = Discount(
        id=1, name="Priority 1", type=DiscountType.PERCENTAGE, is_stackable=False, priority=1
    )
    low_priority = Discount(
        id=2, name="Priority 5", type=DiscountType.FLAT, is_stackable=False, priority=5
    )

    # Even though low_priority has a bigger discount amount, priority wins.
    outcome = RuleEngine().resolve(
        [_result(high_priority, 10.0), _result(low_priority, 50.0)]
    )

    assert len(outcome.selected) == 1
    assert outcome.selected[0].discount.id == 1
    assert outcome.total_discount == 10.0


def test_rule_engine_breaks_priority_ties_by_highest_amount() -> None:
    a = Discount(id=1, name="A", type=DiscountType.PERCENTAGE, is_stackable=False, priority=1)
    b = Discount(id=2, name="B", type=DiscountType.FLAT, is_stackable=False, priority=1)

    outcome = RuleEngine().resolve([_result(a, 10.0), _result(b, 25.0)])

    assert outcome.selected[0].discount.id == 2
    assert outcome.total_discount == 25.0


def test_rule_engine_combines_stackable_with_one_best_non_stackable() -> None:
    stackable = Discount(id=1, name="Stack", type=DiscountType.PERCENTAGE, is_stackable=True)
    non_stackable_1 = Discount(
        id=2, name="NS1", type=DiscountType.FLAT, is_stackable=False, priority=1
    )
    non_stackable_2 = Discount(
        id=3, name="NS2", type=DiscountType.FLAT, is_stackable=False, priority=2
    )

    outcome = RuleEngine().resolve(
        [_result(stackable, 5.0), _result(non_stackable_1, 15.0), _result(non_stackable_2, 100.0)]
    )

    assert outcome.total_discount == 20.0  # 5 (stackable) + 15 (priority-1 non-stackable)
    assert {r.discount.id for r in outcome.selected} == {1, 2}


def test_rule_engine_ignores_non_applied_results() -> None:
    d1 = Discount(id=1, name="Not Applied", type=DiscountType.PERCENTAGE, is_stackable=True)

    outcome = RuleEngine().resolve([_result(d1, 0.0, applied=False)])

    assert outcome.selected == []
    assert outcome.total_discount == 0.0


def test_strategy_factory_returns_correct_strategy_type() -> None:
    discount = Discount(id=1, name="Test", type=DiscountType.PERCENTAGE, value=10)
    strategy = StrategyFactory.create(discount)
    assert isinstance(strategy, PercentageDiscountStrategy)


def test_strategy_factory_raises_for_unregistered_type() -> None:
    discount = Discount(id=1, name="Bogus", type="NOT_A_REAL_TYPE", value=10)
    with pytest.raises(BadRequestException):
        StrategyFactory.create(discount)
