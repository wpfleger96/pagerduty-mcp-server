"""Pydantic models for PagerDuty On-Calls."""

from .common import PagerDutyBaseModel, Reference


class Oncall(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty On-Call."""

    # All fields optional to handle various API response contexts
    user: Reference | None = None
    schedule: Reference | None = None
    escalation_policy: Reference | None = None
    escalation_level: int | None = None
    start: str | None = None
    end: str | None = None
