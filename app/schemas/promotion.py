"""Pydantic schemas for Promotion request/response payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromotionBase(BaseModel):
    """Fields shared by create and update payloads."""

    discount_id: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    active: bool = True

    @model_validator(mode="after")
    def validate_date_window(self) -> "PromotionBase":
        """Ensure the promotional window is chronologically valid."""

        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PromotionCreate(PromotionBase):
    """Payload for creating a new promotion."""

    pass


class PromotionRead(PromotionBase):
    """Representation of a promotion returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
