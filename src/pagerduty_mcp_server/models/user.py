"""Pydantic models for PagerDuty Users."""

from typing import Any

from pydantic import Field

from .common import PagerDutyBaseModel, TypedReference


class NotificationRule(PagerDutyBaseModel):
    """A notification rule for a user."""

    id: str
    type: str

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    summary: str | None = Field(
        None, exclude=True, description="Excluded: Human-readable summary"
    )
    self: str | None = Field(None, exclude=True, description="Excluded: API URL")
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")


class User(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty User.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: str | None = None
    email: str | None = None
    type: str | None = None

    # Optional fields - can be None in API responses
    description: str | None = None

    # Collections - present but can be empty
    teams: list[TypedReference] = []
    contact_methods: list[TypedReference] = []
    notification_rules: list[NotificationRule] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    time_zone: str | None = Field(
        None, exclude=True, description="Excluded: User's time zone"
    )
    color: str | None = Field(
        None, exclude=True, description="Excluded: User's color preference"
    )
    avatar_url: str | None = Field(
        None, exclude=True, description="Excluded: User's avatar URL"
    )
    billed: bool | None = Field(
        None, exclude=True, description="Excluded: Whether user is billed"
    )
    role: str | None = Field(
        None, exclude=True, description="Excluded: User's account role"
    )
    invitation_sent: bool | None = Field(
        None, exclude=True, description="Excluded: Whether invitation was sent"
    )
    job_title: str | None = Field(
        None, exclude=True, description="Excluded: User's job title"
    )
    coordinated_incidents: list[dict[str, Any]] | None = Field(
        None, exclude=True, description="Excluded: Coordinated incidents list"
    )
    locale: str | None = Field(
        None, exclude=True, description="Excluded: User's locale preference"
    )
    summary: str | None = Field(
        None, exclude=True, description="Excluded: Usually same as name"
    )
    self: str | None = Field(None, exclude=True, description="Excluded: API URL")
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")
