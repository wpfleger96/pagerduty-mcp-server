"""Pydantic models for PagerDuty On-Calls."""

from typing import Optional

from .common import PagerDutyBaseModel, Reference


class Oncall(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty On-Call."""

    # All fields optional to handle various API response contexts
    user: Optional[Reference] = None
    schedule: Optional[Reference] = None
    escalation_policy: Optional[Reference] = None
    escalation_level: Optional[int] = None
    start: Optional[str] = None
    end: Optional[str] = None
