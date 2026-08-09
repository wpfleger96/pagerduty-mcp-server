"""Pydantic models for PagerDuty Teams."""

from pydantic import Field

from .common import PagerDutyBaseModel


class TeamParent(PagerDutyBaseModel):
    """A parent team reference."""

    id: str
    type: str | None = None


class Team(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Team.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: str | None = None

    # Optional fields - can be None in API responses
    description: str | None = None
    parent: TeamParent | None = None

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: str | None = Field(None, exclude=True, description="Excluded: Always 'team'")
    summary: str | None = Field(
        None, exclude=True, description="Excluded: Usually same as name"
    )
    self: str | None = Field(None, exclude=True, description="Excluded: API URL")
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")
    default_role: str | None = Field(
        None, exclude=True, description="Excluded: Default member role"
    )
