"""Generic mapping helpers between ORM models and plain dictionaries.

FastAPI/Pydantic already handles ORM -> schema mapping automatically
via ``model_config = ConfigDict(from_attributes=True)`` on the
``*Read`` schemas (see ``app.schemas``), so these helpers are for the
remaining cases: ad-hoc serialization (e.g. logging a model's state)
and turning a validated Pydantic payload into ORM constructor kwargs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def model_to_dict(instance: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Serialize a SQLAlchemy ORM instance's column values to a dict.

    Args:
        instance: Any SQLAlchemy declarative model instance.
        exclude: Optional set of column names to omit from the result.

    Returns:
        dict[str, Any]: Mapping of column name to its current value.
    """

    exclude = exclude or set()
    mapper = instance.__mapper__
    return {
        column.key: getattr(instance, column.key)
        for column in mapper.column_attrs
        if column.key not in exclude
    }


def schema_to_kwargs(payload: BaseModel, exclude_unset: bool = False) -> dict[str, Any]:
    """Convert a Pydantic schema instance into ORM constructor kwargs.

    Args:
        payload: A validated Pydantic model (typically a ``*Create``
            or ``*Update`` schema).
        exclude_unset: If True, only fields explicitly supplied by the
            caller are included -- useful for building ``PATCH``-style
            partial updates.

    Returns:
        dict[str, Any]: Field name/value pairs suitable for passing to
        an ORM model's constructor or for iterating with ``setattr``.
    """

    return payload.model_dump(exclude_unset=exclude_unset)
