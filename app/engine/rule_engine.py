"""Rule Engine: decides *which* evaluated discounts make it onto the bill.

This module is deliberately free of any database or HTTP concerns --
it operates purely on ``DiscountResult`` objects already produced by
the Strategy layer. That separation makes the tricky "stackable vs.
non-stackable, priority-ordered" business rule trivial to unit test
with plain Python objects and no database fixture.

Business rule (per the assignment spec):
    * Discounts that did not qualify (``applied=False``) are ignored.
    * All qualifying **stackable** discounts are combined (summed).
    * Among qualifying **non-stackable** discounts, only one is
      selected: the one respecting priority first (lower
      ``priority`` number wins), and the highest discount amount as
      the tie-breaker among equal-priority candidates.
    * The final discount list returned is the stackable discounts plus
      the single chosen non-stackable discount (if any).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.strategies.base_strategy import DiscountResult


@dataclass(frozen=True)
class RuleEngineOutcome:
    """The set of discounts the Rule Engine decided to apply.

    Attributes:
        selected: The final, ordered list of ``DiscountResult`` objects
            that should be deducted from the cart subtotal.
        total_discount: Sum of ``selected[*].amount``.
    """

    selected: list[DiscountResult]
    total_discount: float


class RuleEngine:
    """Applies stackability and priority rules to evaluated discounts."""

    def resolve(self, results: list[DiscountResult]) -> RuleEngineOutcome:
        """Select the winning combination of discounts.

        Args:
            results: Every ``DiscountResult`` produced by evaluating
                all active, non-expired promotions against the cart
                (both applied and non-applied).

        Returns:
            RuleEngineOutcome: The final discounts to apply and their
            combined total.
        """

        qualifying = [r for r in results if r.applied and r.amount > 0]

        stackable = [r for r in qualifying if r.discount.is_stackable]
        non_stackable = [r for r in qualifying if not r.discount.is_stackable]

        selected: list[DiscountResult] = list(stackable)

        best_non_stackable = self._select_best_non_stackable(non_stackable)
        if best_non_stackable is not None:
            selected.append(best_non_stackable)

        total_discount = round(sum(r.amount for r in selected), 2)
        return RuleEngineOutcome(selected=selected, total_discount=total_discount)

    @staticmethod
    def _select_best_non_stackable(
        candidates: list[DiscountResult],
    ) -> DiscountResult | None:
        """Pick the single best non-stackable discount, if any qualify.

        Selection is by lowest ``priority`` value first (a lower
        number means the discount was configured with higher
        priority); ties are broken by the highest discount ``amount``
        so the customer always gets the most favorable outcome among
        equally-prioritized promotions.

        Args:
            candidates: Qualifying, non-stackable discount results.

        Returns:
            DiscountResult | None: The winning result, or ``None`` if
            ``candidates`` is empty.
        """

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda r: (r.discount.priority, -r.amount),
        )
