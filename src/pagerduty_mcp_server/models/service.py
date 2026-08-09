"""Pydantic models for PagerDuty Services."""

from pydantic import Field

from .common import PagerDutyBaseModel, Reference


class Service(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Service.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    name: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    # Optional fields - can be None in API responses
    description: str | None = None

    # Collections - present but can be empty
    teams: list[Reference] = []
    integrations: list[Reference] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    html_url: str | None = Field(None, exclude=True, description="Excluded: Web UI URL")
