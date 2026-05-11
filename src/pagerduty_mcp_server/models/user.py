"""Pydantic models for PagerDuty Users."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .common import PagerDutyBaseModel, TypedReference


class NotificationRule(PagerDutyBaseModel):
    """A notification rule for a user."""

    id: str
    type: str

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    summary: Optional[str] = Field(
        None, exclude=True, description="Excluded: Human-readable summary"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )


class User(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty User.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None

    # Optional fields - can be None in API responses
    description: Optional[str] = None

    # Collections - present but can be empty
    teams: List[TypedReference] = []
    contact_methods: List[TypedReference] = []
    notification_rules: List[NotificationRule] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    time_zone: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's time zone"
    )
    color: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's color preference"
    )
    avatar_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's avatar URL"
    )
    billed: Optional[bool] = Field(
        None, exclude=True, description="Excluded: Whether user is billed"
    )
    role: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's account role"
    )
    invitation_sent: Optional[bool] = Field(
        None, exclude=True, description="Excluded: Whether invitation was sent"
    )
    job_title: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's job title"
    )
    coordinated_incidents: Optional[List[Dict[str, Any]]] = Field(
        None, exclude=True, description="Excluded: Coordinated incidents list"
    )
    locale: Optional[str] = Field(
        None, exclude=True, description="Excluded: User's locale preference"
    )
    summary: Optional[str] = Field(
        None, exclude=True, description="Excluded: Usually same as name"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
