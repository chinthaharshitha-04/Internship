"""Small, generic helper functions used across the codebase."""

from __future__ import annotations

from datetime import datetime, timezone


def round_currency(amount: float) -> float:
    """Round a monetary amount to 2 decimal places.

    Centralizing this avoids subtle inconsistencies from different
    modules rounding at different precisions (e.g. one strategy using
    ``round(x, 2)`` and another truncating), which could otherwise
    cause the sum of applied discounts to not add up exactly to
    ``subtotal - final_amount``.

    Args:
        amount: The raw monetary value to round.

    Returns:
        float: ``amount`` rounded to 2 decimal places.
    """

    return round(amount, 2)


def utc_now() -> datetime:
    """Return the current UTC timestamp, timezone-naive.

    Kept timezone-naive to match the ``DateTime`` columns used by
    ``Promotion.start_date`` / ``end_date`` (SQLite has no native
    timezone-aware datetime type), ensuring comparisons against
    database values remain valid.
    """

    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_within_window(reference: datetime, start: datetime, end: datetime) -> bool:
    """Check whether ``reference`` falls within ``[start, end]`` inclusive.

    Args:
        reference: The timestamp to check.
        start: Window start (inclusive).
        end: Window end (inclusive).

    Returns:
        bool: True if ``start <= reference <= end``.
    """

    return start <= reference <= end


def safe_percentage(value: float, total: float) -> float:
    """Compute ``value`` as a percentage of ``total``, guarding against division by zero.

    Args:
        value: The numerator.
        total: The denominator.

    Returns:
        float: ``(value / total) * 100``, or ``0.0`` if ``total`` is
        zero.
    """

    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)
