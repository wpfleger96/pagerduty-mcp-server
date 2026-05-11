"""Pydantic models for PagerDuty Teams."""

from typing import Optional

from pydantic import Field

from .common import PagerDutyBaseModel


class TeamParent(PagerDutyBaseModel):
    """A parent team reference."""

    id: str
    type: Optional[str] = None


class Team(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Team.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: Optional[str] = None

    # Optional fields - can be None in API responses
    description: Optional[str] = None
    parent: Optional[TeamParent] = None

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: Always 'team'"
    )
    summary: Optional[str] = Field(
        None, exclude=True, description="Excluded: Usually same as name"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
    default_role: Optional[str] = Field(
        None, exclude=True, description="Excluded: Default member role"
    )
